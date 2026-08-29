"""Domain collector - DNS, TLS, HTTP intelligence."""

import asyncio
import socket
import ssl
from datetime import datetime, timezone
from typing import Dict, Any, List
import httpx
from urllib.parse import urlparse

from packages.collectors.base import BaseCollector, CollectorContext, CollectorResult
from packages.models.schemas import TargetType, EntityType, SourceType, RelationshipType
from packages.common.utils import validate_domain, normalize_domain

logger = logging.getLogger(__name__)


class DomainCollector(BaseCollector):
    """Collect public domain intelligence."""

    name = "domain"
    description = "Collect DNS, TLS, and HTTP intelligence for domains"
    target_types = [TargetType.DOMAIN]
    timeout = 30

    async def _collect_impl(self, context: CollectorContext) -> Dict[str, Any]:
        """Collect domain intelligence."""
        domain = normalize_domain(context.target.value)

        if not validate_domain(domain):
            return {"errors": ["Invalid domain format"]}

        entities: List[Any] = []
        relationships: List[Any] = []
        evidence: List[Any] = []
        errors: List[str] = []

        # DNS records
        try:
            dns_data = await self._collect_dns(domain)
            if dns_data:
                # Create domain entity
                domain_entity = self.create_entity(
                    EntityType.DOMAIN,
                    domain,
                    name=domain,
                    confidence=0.9,
                    metadata={"dns": dns_data},
                )
                entities.append(domain_entity)

                # Create evidence
                evidence.append(self.create_evidence(
                    context=context,
                    observation=f"DNS records for {domain}",
                    raw_data={"dns": dns_data, "domain": domain},
                    entity_id=domain_entity.id,
                    confidence=1.0,
                    source_type=SourceType.DNS,
                ))

                # Create subdomain entities
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
            if cert_data:
                cert_entity = self.create_entity(
                    EntityType.CERTIFICATE,
                    cert_data.get("fingerprint", ""),
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
                # Create URL entity
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

    async def _collect_dns(self, domain: str) -> Dict[str, Any]:
        """Collect DNS records."""
        records = {
            "a": [],
            "aaaa": [],
            "mx": [],
            "txt": [],
            "ns": [],
            "cname": [],
        }

        try:
            loop = asyncio.get_event_loop()
            for record_type in ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]:
                try:
                    answers = await loop.getaddrinfo(domain, None)
                    if record_type == "A":
                        for addr in answers:
                            ip = addr[4][0]
                            if ":" not in ip and ip not in records["a"]:
                                records["a"].append(ip)
                    elif record_type == "AAAA":
                        for addr in answers:
                            ip = addr[4][0]
                            if ":" in ip and ip not in records["aaaa"]:
                                records["aaaa"].append(ip)
                except Exception:
                    pass

            # Get MX records via dnspython library
            try:
                from dns import resolver
                resolver_cache = {}
                for rtype in ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]:
                    try:
                        answers = resolver.resolve(domain, rtype)
                        if rtype == "A":
                            records["a"] = [r.address for r in answers]
                        elif rtype == "AAAA":
                            records["aaaa"] = [r.address for r in answers]
                        elif rtype == "MX":
                            records["mx"] = [{"exchange": str(r.exchange), "preference": r.preference} for r in answers]
                        elif rtype == "TXT":
                            records["txt"] = [str(r) for r in answers]
                        elif rtype == "NS":
                            records["ns"] = [str(r) for r in answers]
                        elif rtype == "CNAME":
                            records["cname"] = [str(r) for r in answers]
                    except Exception:
                        pass
            except ImportError:
                pass

        except Exception as e:
            self.log.warning(f"DNS resolution error for {domain}: {e}")

        return records

    async def _collect_certificate(self, domain: str) -> Dict[str, Any]:
        """Collect TLS certificate information."""
        cert_data = {
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
                    cert = ssock.getpeercert(True)
                    if cert:
                        cert_dict = ssl._ssl._test_decode_cert(cert)
                        issuer = cert_dict.get("issuer", ())
                        subject = cert_dict.get("subject", ())
                        cert_data["issuer"] = dict((k, v) for i in issuer for k, v in i) if issuer else None
                        cert_data["subject"] = dict((k, v) for i in subject for k, v in i) if subject else None
                        cert_data["valid_from"] = cert_dict.get("notBefore")
                        cert_data["valid_to"] = cert_dict.get("notAfter")
                        cert_data["fingerprint"] = cert.get("fingerprint").hex() if cert.get("fingerprint") else None
                        cert_data["san"] = cert_dict.get("subjectAltName", [])

        except Exception as e:
            self.log.debug(f"Certificate collection failed for {domain}: {e}")

        return cert_data

    async def _collect_http(self, domain: str) -> Dict[str, Any]:
        """Collect HTTP intelligence."""
        http_data = {
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

                    # Extract title
                    if "text/html" in response.headers.get("content-type", ""):
                        body = response.text.lower()
                        if "<title>" in body and "</title>" in body:
                            title_start = body.find("<title>") + 7
                            title_end = body.find("</title>")
                            http_data["page_title"] = response.text[title_start:title_end].strip()

                    # Record redirects
                    if response.history:
                        http_data["redirects"] = [
                            {"location": str(req.url), "status": req.status_code}
                            for req in response.history
                        ]

                    break
                except Exception as e:
                    self.log.debug(f"HTTP collection failed for {scheme}://{domain}: {e}")

        return http_data