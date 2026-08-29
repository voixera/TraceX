"""URL collector - analyze URLs and web pages."""

import hashlib
import logging
import re
from typing import Any
from urllib.parse import urlparse

import httpx

from packages.collectors.base import BaseCollector, CollectorContext
from packages.common.utils import validate_url
from packages.models.schemas import EntityType, SourceType, TargetType

logger = logging.getLogger(__name__)


class URLCollector(BaseCollector):
    """Collect URL and web page intelligence."""

    name = "url"
    description = "Collect HTTP, headers, redirects, and page analysis for URLs"
    target_types = [TargetType.URL]
    timeout = 30

    async def _collect_impl(self, context: CollectorContext) -> dict[str, Any]:
        """Collect URL intelligence."""
        url = context.target.value

        if not validate_url(url):
            return {"errors": ["Invalid URL format"]}

        entities: list[Any] = []
        relationships: list[Any] = []
        evidence: list[Any] = []
        errors: list[str] = []

        # HTTP analysis
        try:
            http_data = await self._collect_http(url)
            if http_data:
                url_entity = self.create_entity(
                    EntityType.URL,
                    url,
                    name=f"URL: {url}",
                    confidence=1.0,
                    metadata={"http": http_data},
                )
                entities.append(url_entity)

                evidence.append(self.create_evidence(
                    context=context,
                    observation=f"HTTP analysis for {url}",
                    raw_data={"url": url, "http": http_data},
                    entity_id=url_entity.id,
                    confidence=0.9,
                    source_type=SourceType.HTTP,
                ))

                parsed = urlparse(url)
                if parsed.netloc:
                    url_entity.metadata["domain"] = parsed.netloc.split(":")[0].lower()

        except Exception as e:
            errors.append(f"HTTP collection failed: {e}")

        # Analyze robots.txt
        try:
            robots_data = await self._collect_robots(url)
            if robots_data:
                evidence.append(self.create_evidence(
                    context=context,
                    observation=f"robots.txt for {url}",
                    raw_data={"url": url, "robots": robots_data},
                    confidence=0.8,
                    source_type=SourceType.HTTP,
                ))
        except Exception as e:
            errors.append(f"robots.txt collection failed: {e}")

        # Analyze sitemap
        try:
            sitemap_data = await self._collect_sitemap(url)
            if sitemap_data:
                evidence.append(self.create_evidence(
                    context=context,
                    observation=f"sitemap for {url}",
                    raw_data={"url": url, "sitemap": sitemap_data},
                    confidence=0.8,
                    source_type=SourceType.HTTP,
                ))
        except Exception as e:
            errors.append(f"sitemap collection failed: {e}")

        return {
            "entities": entities,
            "relationships": relationships,
            "evidence": evidence,
            "errors": errors,
        }

    async def _collect_http(self, url: str) -> dict[str, Any]:
        """Collect HTTP data for URL."""
        http_data: dict[str, Any] = {
            "status_code": None,
            "headers": {},
            "redirects": [],
            "response_time_ms": None,
            "page_title": None,
            "body_hash": None,
            "content_length": None,
            "canonical_url": None,
        }

        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            try:
                import time
                start = time.time()
                response = await client.get(url)
                http_data["status_code"] = response.status_code
                http_data["headers"] = dict(response.headers)
                http_data["response_time_ms"] = (time.time() - start) * 1000
                http_data["content_length"] = len(response.content)

                if response.content:
                    http_data["body_hash"] = hashlib.sha256(response.content).hexdigest()

                content_type = response.headers.get("content-type", "")
                if "text/html" in content_type.lower():
                    body = response.text
                    title_match = re.search(r"<title[^>]*>(.*?)</title>", body, re.IGNORECASE | re.DOTALL)
                    if title_match:
                        http_data["page_title"] = title_match.group(1).strip()

                    canonical_match = re.search(
                        r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']*)["\'][^>]*>',
                        body, re.IGNORECASE,
                    )
                    if canonical_match:
                        http_data["canonical_url"] = canonical_match.group(1)

                if response.history:
                    http_data["redirects"] = [
                        {
                            "url": str(req.url),
                            "status": req.status_code,
                            "location": req.headers.get("location", ""),
                        }
                        for req in response.history
                    ]

            except Exception as e:
                self.log.debug(f"HTTP request failed for {url}: {e}")

        return http_data

    async def _collect_robots(self, url: str) -> dict[str, Any]:
        """Collect robots.txt data."""
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        async with httpx.AsyncClient(timeout=5) as client:
            try:
                response = await client.get(robots_url)
                if response.status_code == 200:
                    return {
                        "url": robots_url,
                        "content": response.text,
                        "lines": response.text.split("\n"),
                        "disallow_rules": [
                            line.split(":", 1)[1].strip()
                            for line in response.text.split("\n")
                            if line.lower().startswith("disallow:")
                        ],
                        "allow_rules": [
                            line.split(":", 1)[1].strip()
                            for line in response.text.split("\n")
                            if line.lower().startswith("allow:")
                        ],
                        "sitemap": [
                            line.split(":", 1)[1].strip()
                            for line in response.text.split("\n")
                            if line.lower().startswith("sitemap:")
                        ],
                    }
            except Exception:
                pass

        return {}

    async def _collect_sitemap(self, url: str) -> dict[str, Any]:
        """Collect sitemap data."""
        parsed = urlparse(url)
        sitemap_urls = [
            f"{parsed.scheme}://{parsed.netloc}/sitemap.xml",
            f"{parsed.scheme}://{parsed.netloc}/sitemap_index.xml",
        ]

        async with httpx.AsyncClient(timeout=10) as client:
            for sitemap_url in sitemap_urls:
                try:
                    response = await client.get(sitemap_url)
                    if response.status_code == 200 and response.content:
                        content = response.text
                        urls_found = re.findall(r"<loc>([^<]+)</loc>", content)
                        return {
                            "url": sitemap_url,
                            "content": content,
                            "urls": urls_found[:100],
                            "url_count": len(urls_found),
                        }
                except Exception:
                    pass

        return {}
