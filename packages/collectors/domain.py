"""Domain collector - DNS, TLS, HTTP intelligence."""

import asyncio
import logging
import socket
import ssl
from typing import Any

import httpx

from packages.collectors.base import BaseCollector, CollectorContext
from packages.common.utils import normalize_domain, validate_domain
from packages.models.schemas import EntityType, SourceType, TargetType

logger = logging.getLogger(__name__)


class DomainCollector(BaseCollector):
    """Collect public domain intelligence."""

    name = "domain"
    description = "Collect DNS, TLS, and HTTP intelligence for domains"
    target_types = [TargetType.DOMAIN]
    timeout = 30

    async def _collect_impl(self, context: CollectorContext) -> dict[str, Any]:
        """Collect domain intelligence."""
        domain = normalize_domain(context.target.value)

        if not validate_domain(domain):
            return {"errors": ["Invalid domain format"]}

        entities: list[Any] = []
        relationships: list[Any] = []
        evidence: list[Any] = []
        errors: list[str] = []

        # DNS records
        try:
            dns_data = await self._collect_dns(domain)
            if dns_data:
                domain_entity = self.create_entity(
                    EntityType.DOMAIN,
                    domain,
                    name=domain,
                    confidence=0.9,
                    metadata={"dns": dns_data},
                )
                entities.append(domain_entity)

                evidence.append(self.create_evidence(
                    context=context,
                    observation=f"DNS records for {domain}",
                    raw_data={"dns": dns_data, "domain": domain},
                    entity_id=domain_entity.id,
                    confidence=1.0,
                    source_type=SourceType.DNS,
                ))

                for subdomain in dns_data.get("a", []) + dns_data.get("aaaa", []):
                    if subdomain and subdomain != domain:
                        sub_entity = self.create_entity(
                            EntityType.SUBDOMAIN,
                            subdomain,
                            name=subdomain,
                            confidence=0.8,
                            metadata={"resolved_from": domain},
                        )
                        entities.append(sub_entity)

        except Exception as e:
            errors.append(f"DNS collection failed: {e}")

        # TLS certificate
        try:
            cert_data = await self._collect_certificate(domain)
            if cert_data and cert_data.get("subject"):
                cert_entity = self.create_entity(
                    EntityType.CERTIFICATE,
                    cert_data.get("fingerprint", cert_data.get("subject", "")),
                    name=f"Certificate for {domain}",
                    confidence=1.0,
                    metadata=cert_data,
                )
                entities.append(cert_entity)

                evidence.append(self.create_evidence(
                    context=context,
                    observation=f"TLS certificate for {domain}",
                    raw_data={"tls": cert_data, "domain": domain},
                    entity_id=cert_entity.id,
                    confidence=1.0,
                    source_type=SourceType.CERTIFICATE,
                ))

        except Exception as e:
            errors.append(f"TLS collection failed: {e}")

        # HTTP analysis
        try:
            http_data = await self._collect_http(domain)
            if http_data:
                url_entity = self.create_entity(
                    EntityType.URL,
                    f"https://{domain}",
                    name=f"Website for {domain}",
                    confidence=0.9,
                    metadata={"http": http_data},
                )
                entities.append(url_entity)

                evidence.append(self.create_evidence(
                    context=context,
                    observation=f"HTTP analysis for {domain}",
                    raw_data={"http": http_data, "domain": domain},
                    entity_id=url_entity.id,
                    confidence=0.9,
                    source_type=SourceType.HTTP,
                ))

        except Exception as e:
            errors.append(f"HTTP collection failed: {e}")

        return {
            "entities": entities,
            "relationships": relationships,
            "evidence": evidence,
            "errors": errors,
        }

    async def _collect_dns(self, domain: str) -> dict[str, Any]:
        """Collect DNS records."""
        records: dict[str, list[Any]] = {
            "a": [], "aaaa": [], "mx": [], "txt": [], "ns": [], "cname": [],
        }

        try:
            loop = asyncio.get_event_loop()
            try:
                answers = await loop.getaddrinfo(domain, None)
                for addr in answers:
                    ip = str(addr[4][0])
                    if ":" not in ip and ip not in records["a"]:
                        records["a"].append(ip)
                    elif ":" in ip and ip not in records["aaaa"]:
                        records["aaaa"].append(ip)
            except Exception:
                pass

            try:
                import dns.resolver
                for rtype in ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]:
                    try:
                        dns_answers = dns.resolver.resolve(domain, rtype)
                        if rtype == "A":
                            records["a"] = [str(r) for r in dns_answers]
                        elif rtype == "AAAA":
                            records["aaaa"] = [str(r) for r in dns_answers]
                        elif rtype == "MX":
                            records["mx"] = [
                                {"exchange": str(r.exchange), "preference": r.preference}
                                for r in dns_answers
                            ]
                        elif rtype == "TXT":
                            records["txt"] = [str(r) for r in dns_answers]
                        elif rtype == "NS":
                            records["ns"] = [str(r) for r in dns_answers]
                        elif rtype == "CNAME":
                            records["cname"] = [str(r) for r in dns_answers]
                    except Exception:
                        pass
            except ImportError:
                pass

        except Exception as e:
            self.log.warning(f"DNS resolution error for {domain}: {e}")

        return records

    async def _collect_certificate(self, domain: str) -> dict[str, Any]:
        """Collect TLS certificate information."""
        cert_data: dict[str, Any] = {
            "issuer": None,
            "subject": None,
            "valid_from": None,
            "valid_to": None,
            "fingerprint": None,
            "san": [],
        }

        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert_der = ssock.getpeercert(binary_form=True)
                    if cert_der:
                        import hashlib
                        cert_data["fingerprint"] = hashlib.sha256(cert_der).hexdigest()
                        cert_data["subject"] = domain
                        cert_data["issuer"] = "TLS/SSL"

        except Exception as e:
            self.log.debug(f"Certificate collection failed for {domain}: {e}")

        return cert_data

    async def _collect_http(self, domain: str) -> dict[str, Any]:
        """Collect HTTP intelligence."""
        http_data: dict[str, Any] = {
            "status_code": None,
            "headers": {},
            "redirects": [],
            "response_time_ms": None,
            "page_title": None,
            "body_hash": None,
        }

        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            for scheme in ["https", "http"]:
                try:
                    import time
                    start = time.time()
                    response = await client.get(f"{scheme}://{domain}")
                    http_data["status_code"] = response.status_code
                    http_data["headers"] = dict(response.headers)
                    http_data["response_time_ms"] = (time.time() - start) * 1000

                    if "text/html" in response.headers.get("content-type", ""):
                        body = response.text.lower()
                        if "<title>" in body and "</title>" in body:
                            title_start = body.find("<title>") + 7
                            title_end = body.find("</title>")
                            http_data["page_title"] = response.text[title_start:title_end].strip()

                    if response.history:
                        http_data["redirects"] = [
                            {"location": str(req.url), "status": req.status_code}
                            for req in response.history
                        ]

                    break
                except Exception as e:
                    self.log.debug(f"HTTP collection failed for {scheme}://{domain}: {e}")

        return http_data
