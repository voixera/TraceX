"""TraceX Relationship Engine module."""

import logging
from datetime import UTC, datetime
from typing import Any

from packages.common.utils import generate_id
from packages.models.schemas import (
    Entity,
    EntityType,
    Relationship,
    RelationshipType,
)

logger = logging.getLogger(__name__)


class RelationshipEngine:
    """Build relationships between entities."""

    def __init__(self):
        self.rules: list[Any] = []
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register default relationship inference rules."""
        self.rules.append(self._github_owns_repo)
        self.rules.append(self._domain_has_subdomain)
        self.rules.append(self._url_belongs_to_domain)
        self.rules.append(self._certificate_issued_to_domain)
        self.rules.append(self._possible_username_match)

    def infer_relationships(self, entities: list[Entity]) -> list[Relationship]:
        """Infer relationships from entity list."""
        relationships: list[Relationship] = []

        for rule in self.rules:
            try:
                relationships.extend(rule(entities))
            except Exception as e:
                logger.warning(f"Relationship rule failed: {e}")

        return relationships

    def _github_owns_repo(self, entities: list[Entity]) -> list[Relationship]:
        """GitHub account owns repository."""
        accounts = [e for e in entities if e.entity_type == EntityType.USERNAME and "github" in str(e.metadata.get("source", ""))]
        repos = [e for e in entities if e.entity_type == EntityType.REPOSITORY]

        rels: list[Relationship] = []
        for account in accounts:
            for repo in repos:
                if repo.metadata.get("owner") == account.value:
                    rels.append(Relationship(
                        id=generate_id("rel_"),
                        source_id=account.id,
                        target_id=repo.id,
                        relationship_type=RelationshipType.OWNS,
                        confidence=1.0,
                        source_reference="github_api",
                        observed_at=datetime.now(UTC),
                    ))
        return rels

    def _domain_has_subdomain(self, entities: list[Entity]) -> list[Relationship]:
        """Domain has subdomain."""
        domains = [e for e in entities if e.entity_type == EntityType.DOMAIN]
        subdomains = [e for e in entities if e.entity_type == EntityType.SUBDOMAIN]

        rels: list[Relationship] = []
        for domain in domains:
            for sub in subdomains:
                if sub.value.endswith(f".{domain.value}"):
                    rels.append(Relationship(
                        id=generate_id("rel_"),
                        source_id=domain.id,
                        target_id=sub.id,
                        relationship_type=RelationshipType.HOSTS,
                        confidence=1.0,
                        source_reference="dns",
                        observed_at=datetime.now(UTC),
                    ))
        return rels

    def _url_belongs_to_domain(self, entities: list[Entity]) -> list[Relationship]:
        """URL belongs to domain."""
        from urllib.parse import urlparse

        urls = [e for e in entities if e.entity_type == EntityType.URL]
        domains = {e.value: e for e in entities if e.entity_type == EntityType.DOMAIN}

        rels: list[Relationship] = []
        for url_entity in urls:
            try:
                parsed = urlparse(url_entity.value)
                domain_value = parsed.netloc.split(":")[0].lower()
                if domain_value in domains:
                    rels.append(Relationship(
                        id=generate_id("rel_"),
                        source_id=domains[domain_value].id,
                        target_id=url_entity.id,
                        relationship_type=RelationshipType.HOSTS,
                        confidence=0.9,
                        source_reference="url_analysis",
                        observed_at=datetime.now(UTC),
                    ))
            except Exception:
                pass
        return rels

    def _certificate_issued_to_domain(self, entities: list[Entity]) -> list[Relationship]:
        """Certificate issued to domain."""
        certs = [e for e in entities if e.entity_type == EntityType.CERTIFICATE]
        domains = {e.value: e for e in entities if e.entity_type == EntityType.DOMAIN}

        rels: list[Relationship] = []
        for cert in certs:
            for domain_value in cert.metadata.get("domains", []):
                if domain_value in domains:
                    rels.append(Relationship(
                        id=generate_id("rel_"),
                        source_id=domains[domain_value].id,
                        target_id=cert.id,
                        relationship_type=RelationshipType.HOSTS,
                        confidence=1.0,
                        source_reference="tls_certificate",
                        observed_at=datetime.now(UTC),
                    ))
        return rels

    def _possible_username_match(self, entities: list[Entity]) -> list[Relationship]:
        """Possible username match across platforms."""
        usernames = [e for e in entities if e.entity_type == EntityType.USERNAME]

        rels: list[Relationship] = []
        for i, u1 in enumerate(usernames):
            for u2 in usernames[i + 1:]:
                if u1.value.lower() == u2.value.lower() and u1.id != u2.id:
                    source1 = u1.metadata.get("source", "")
                    source2 = u2.metadata.get("source", "")
                    if source1 and source2 and source1 != source2:
                        rels.append(Relationship(
                            id=generate_id("rel_"),
                            source_id=u1.id,
                            target_id=u2.id,
                            relationship_type=RelationshipType.POSSIBLE_MATCH,
                            confidence=0.7,
                            source_reference=f"username_match:{source1}:{source2}",
                            observed_at=datetime.now(UTC),
                        ))
        return rels
