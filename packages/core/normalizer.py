"""TraceX Normalizer module."""

from datetime import UTC, datetime
from typing import Any

from packages.common.utils import build_evidence_hash, generate_id
from packages.models.schemas import Entity, EntityType, Evidence, SourceType


class Normalizer:
    """Normalize collector outputs to standard format."""

    def __init__(self):
        self._entity_cache: dict[str, Entity] = {}

    def normalize_entity(self, raw: dict[str, Any], source: str) -> Entity:
        """Normalize raw entity data."""
        entity_type_str = raw.get("entity_type", "domain")
        try:
            entity_type = EntityType(entity_type_str)
        except ValueError:
            entity_type = EntityType.DOMAIN

        value = raw.get("value", "")
        name = raw.get("name", value)
        description = raw.get("description")
        confidence = raw.get("confidence", 1.0)
        metadata = raw.get("metadata", {})
        metadata["source"] = source

        return Entity(
            id=generate_id(f"ent_{entity_type.value}_"),
            entity_type=entity_type,
            value=value,
            name=name,
            description=description,
            confidence=confidence,
            metadata=metadata,
            source_ids=[source],
        )

    def normalize_evidence(
        self,
        raw: dict[str, Any],
        source: str,
        collector: str,
        entity_id: str | None = None,
        case_id: str = "",
    ) -> Evidence:
        """Normalize raw evidence data."""
        observation = raw.get("observation", "")
        raw_data = raw.get("raw_data", {})
        url = raw.get("url")
        source_type_str = raw.get("source_type", "api")
        try:
            source_type = SourceType(source_type_str)
        except ValueError:
            source_type = SourceType.API
        confidence = raw.get("confidence", 1.0)

        evidence_data = {
            "source": source,
            "collector": collector,
            "observation": observation,
            "raw_data": raw_data,
            "url": url,
            "source_type": source_type.value,
            "confidence": confidence,
            "entity_id": entity_id,
        }

        return Evidence(
            id=generate_id("ev_"),
            case_id=case_id,
            entity_id=entity_id,
            source=source,
            source_type=source_type,
            url=url,
            collector=collector,
            observation=observation,
            raw_data=raw_data,
            hash=build_evidence_hash(evidence_data),
            confidence=confidence,
            observed_at=datetime.now(UTC),
        )

    def deduplicate_entities(self, entities: list[Entity]) -> list[Entity]:
        """Deduplicate entities by type and value."""
        seen: dict[str, Entity] = {}
        for entity in entities:
            key = f"{entity.entity_type.value}:{entity.value.lower()}"
            if key not in seen:
                seen[key] = entity
            else:
                existing = seen[key]
                if entity.confidence > existing.confidence:
                    existing.confidence = entity.confidence
                existing.metadata.update(entity.metadata)
                existing.source_ids.extend(entity.source_ids)
        return list(seen.values())

    def normalize_domain_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Normalize domain collector output."""
        normalized = {}
        if "dns" in data:
            dns = data["dns"]
            normalized["dns"] = {
                "a": dns.get("a", []),
                "aaaa": dns.get("aaaa", []),
                "mx": dns.get("mx", []),
                "txt": dns.get("txt", []),
                "ns": dns.get("ns", []),
                "cname": dns.get("cname", []),
            }
        if "tls" in data:
            tls = data["tls"]
            normalized["tls"] = {
                "issuer": tls.get("issuer"),
                "subject": tls.get("subject"),
                "valid_from": tls.get("valid_from"),
                "valid_to": tls.get("valid_to"),
                "fingerprint": tls.get("fingerprint"),
                "san": tls.get("san", []),
            }
        if "http" in data:
            http = data["http"]
            normalized["http"] = {
                "status_code": http.get("status_code"),
                "headers": http.get("headers", {}),
                "redirects": http.get("redirects", []),
                "response_time_ms": http.get("response_time_ms"),
                "page_title": http.get("page_title"),
                "body_hash": http.get("body_hash"),
            }
        if "headers" in data:
            normalized["headers"] = data["headers"]
        return normalized
