"""TraceX Intelligence Core Engine."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

from packages.models.schemas import (
    Target,
    Entity,
    Relationship,
    Evidence,
    CollectorResult,
    TargetType,
    EntityType,
    RelationshipType,
    SourceType,
    ConfidenceLevel,
)
from packages.database.models import Entity as DBEntity, Relationship as DBRelationship, Evidence as DBEvidence
from packages.common.utils import (
    generate_id,
    hash_evidence,
    calculate_confidence_factors,
    get_current_timestamp,
    build_evidence_hash,
)

logger = logging.getLogger(__name__)


@dataclass
class CollectorContext:
    """Context passed to collectors during execution."""

    case_id: str
    target: Target
    config: Dict[str, Any]
    rate_limiter: "RateLimiter"
    session: Any = None


class RateLimiter:
    """Token bucket rate limiter for external APIs."""

    def __init__(self, requests_per_minute: int = 60, requests_per_second: float = 0):
        self.requests_per_minute = requests_per_minute
        self.requests_per_second = requests_per_second
        self._tokens = requests_per_minute
        self._last_refill = datetime.now(timezone.utc)
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire a token, waiting if necessary."""
        async with self._lock:
            now = datetime.now(timezone.utc)
            elapsed = (now - self._last_refill).total_seconds()

            if self.requests_per_second > 0:
                # Per-second refill
                self._tokens = min(self.requests_per_minute, self._tokens + elapsed * self.requests_per_second)
            else:
                # Per-minute refill
                if elapsed >= 60:
                    self._tokens = self.requests_per_minute
                    self._last_refill = now

            if self._tokens >= 1:
                self._tokens -= 1
                return

            # Wait for token
            wait_time = (1 - self._tokens) / (self.requests_per_minute / 60) if self.requests_per_second == 0 else (1 - self._tokens) / self.requests_per_second
            self._tokens = 0

        await asyncio.sleep(max(0.1, wait_time))
        await self.acquire()


class IntelligenceEngine:
    """Main intelligence processing engine."""

    def __init__(
        self,
        db_session_factory: Callable,
        rate_limits: Dict[str, Dict[str, int]] = None,
        collector_timeout: int = 30,
        max_retries: int = 3,
    ):
        self.db_session_factory = db_session_factory
        self.collectors: Dict[str, "BaseCollector"] = {}
        self.rate_limits = rate_limits or {}
        self.collector_timeout = collector_timeout
        self.max_retries = max_retries
        self.normalizer = Normalizer()
        self.relationship_engine = RelationshipEngine()

    def register_collector(self, collector: "BaseCollector") -> None:
        """Register a collector."""
        self.collectors[collector.name] = collector
        logger.info(f"Registered collector: {collector.name}")

    def get_collector(self, name: str) -> Optional["BaseCollector"]:
        """Get collector by name."""
        return self.collectors.get(name)

    def list_collectors(self) -> List[str]:
        """List available collectors."""
        return list(self.collectors.keys())

    async def run_investigation(
        self,
        case_id: str,
        targets: List[Target],
        collectors: List[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """Run investigation on targets with specified collectors."""
        collectors_to_run = collectors or list(self.collectors.keys())
        results = {
            "entities_found": 0,
            "relationships_found": 0,
            "evidence_count": 0,
            "errors": [],
            "collector_results": {},
        }

        total_collectors = len(collectors_to_run)
        for i, collector_name in enumerate(collectors_to_run):
            collector = self.collectors.get(collector_name)
            if not collector:
                results["errors"].append(f"Collector not found: {collector_name}")
                continue

            if progress_callback:
                await progress_callback(i / total_collectors, collector_name)

            # Run collector for each target
            for target in targets:
                try:
                    # Create rate limiter for this collector
                    rate_config = self.rate_limits.get(collector_name, {"requests_per_minute": 60})
                    limiter = RateLimiter(**rate_config)

                    context = CollectorContext(
                        case_id=case_id,
                        target=target,
                        config={},
                        rate_limiter=limiter,
                    )

                    # Execute with timeout and retries
                    result = await self._run_collector_with_retry(collector, context)

                    results["collector_results"][f"{collector_name}:{target.value}"] = result

                    if result.success:
                        results["entities_found"] += len(result.entities)
                        results["relationships_found"] += len(result.relationships)
                        results["evidence_count"] += len(result.evidence)

                        # Store in database
                        await self._store_results(case_id, target.id, result)
                    else:
                        results["errors"].extend(result.errors)

                except Exception as e:
                    logger.error(f"Error running {collector_name} on {target.value}: {e}")
                    results["errors"].append(f"{collector_name}:{target.value}: {str(e)}")

        if progress_callback:
            await progress_callback(1.0, "complete")

        return results

    async def _run_collector_with_retry(
        self,
        collector: "BaseCollector",
        context: CollectorContext,
    ) -> CollectorResult:
        """Run collector with retry logic."""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                await context.rate_limiter.acquire()

                # Run with timeout
                result = await asyncio.wait_for(
                    collector.collect(context),
                    timeout=self.collector_timeout,
                )

                if result.success or attempt == self.max_retries - 1:
                    return result

            except asyncio.TimeoutError:
                last_error = f"Timeout after {self.collector_timeout}s"
            except Exception as e:
                last_error = str(e)

            if attempt < self.max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        return CollectorResult(
            collector=collector.name,
            target=context.target.value,
            target_type=context.target.target_type,
            success=False,
            errors=[last_error or "Unknown error"],
        )

    async def _store_results(
        self,
        case_id: str,
        target_id: str,
        result: CollectorResult,
    ) -> None:
        """Store collector results in database."""
        from packages.database.session import get_session_context
        from packages.common.utils import get_current_timestamp

        async with get_session_context() as session:
            # Store entities
            for entity in result.entities:
                db_entity = DBEntity(
                    id=entity.id,
                    case_id=case_id,
                    entity_type=entity.entity_type,
                    value=entity.value,
                    name=entity.name,
                    description=entity.description,
                    confidence=entity.confidence,
                    metadata=entity.metadata,
                    first_seen=entity.first_seen,
                    last_seen=entity.last_seen,
                    source_ids=entity.source_ids,
                )
                session.add(db_entity)

            # Store relationships
            for rel in result.relationships:
                db_rel = DBRelationship(
                    id=rel.id,
                    case_id=case_id,
                    source_id=rel.source_id,
                    target_id=rel.target_id,
                    relationship_type=rel.relationship_type,
                    confidence=rel.confidence,
                    evidence_ids=rel.evidence_ids,
                    source_reference=rel.source_reference,
                    observed_at=rel.observed_at,
                    metadata=rel.metadata,
                )
                session.add(db_rel)

            # Store evidence
            for evidence in result.evidence:
                db_evidence = DBEvidence(
                    id=evidence.id,
                    case_id=case_id,
                    entity_id=evidence.entity_id,
                    source=evidence.source,
                    source_type=evidence.source_type,
                    url=evidence.url,
                    collector=evidence.collector,
                    observation=evidence.observation,
                    raw_data=evidence.raw_data,
                    hash=evidence.hash,
                    confidence=evidence.confidence,
                    observed_at=evidence.observed_at,
                    metadata=evidence.metadata,
                )
                session.add(db_evidence)

            await session.commit()


class Normalizer:
    """Normalize collector outputs to standard format."""

    def __init__(self):
        self._entity_cache: Dict[str, Entity] = {}

    def normalize_entity(self, raw: Dict[str, Any], source: str) -> Entity:
        """Normalize raw entity data."""
        entity_type = EntityType(raw.get("entity_type", "domain"))
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
        raw: Dict[str, Any],
        source: str,
        collector: str,
        entity_id: Optional[str] = None,
        case_id: str = "",
    ) -> Evidence:
        """Normalize raw evidence data."""
        observation = raw.get("observation", "")
        raw_data = raw.get("raw_data", {})
        url = raw.get("url")
        source_type = SourceType(raw.get("source_type", "api"))
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
            observed_at=datetime.now(timezone.utc),
        )

    def deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Deduplicate entities by type and value."""
        seen = {}
        for entity in entities:
            key = f"{entity.entity_type.value}:{entity.value.lower()}"
            if key not in seen:
                seen[key] = entity
            else:
                # Merge: keep higher confidence, merge metadata
                existing = seen[key]
                if entity.confidence > existing.confidence:
                    existing.confidence = entity.confidence
                existing.metadata.update(entity.metadata)
                existing.source_ids.extend(entity.source_ids)
        return list(seen.values())


class RelationshipEngine:
    """Build relationships between entities."""

    def __init__(self):
        self.rules: List[Callable] = []
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register default relationship inference rules."""
        self.rules.append(self._github_owns_repo)
        self.rules.append(self._domain_has_subdomain)
        self.rules.append(self._url_belongs_to_domain)
        self.rules.append(self._certificate_issued_to_domain)
        self.rules.append(self._possible_username_match)

    def infer_relationships(self, entities: List[Entity]) -> List[Relationship]:
        """Infer relationships from entity list."""
        relationships = []

        for rule in self.rules:
            try:
                relationships.extend(rule(entities))
            except Exception as e:
                logger.warning(f"Relationship rule failed: {e}")

        return relationships

    def _github_owns_repo(self, entities: List[Entity]) -> List[Relationship]:
        """GitHub account owns repository."""
        accounts = [e for e in entities if e.entity_type == EntityType.USERNAME and "github" in e.metadata.get("source", "")]
        repos = [e for e in entities if e.entity_type == EntityType.REPOSITORY]

        rels = []
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
                        observed_at=datetime.now(timezone.utc),
                    ))
        return rels

    def _domain_has_subdomain(self, entities: List[Entity]) -> List[Relationship]:
        """Domain has subdomain."""
        domains = [e for e in entities if e.entity_type == EntityType.DOMAIN]
        subdomains = [e for e in entities if e.entity_type == EntityType.SUBDOMAIN]

        rels = []
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
                        observed_at=datetime.now(timezone.utc),
                    ))
        return rels

    def _url_belongs_to_domain(self, entities: List[Entity]) -> List[Relationship]:
        """URL belongs to domain."""
        from urllib.parse import urlparse

        urls = [e for e in entities if e.entity_type == EntityType.URL]
        domains = {e.value: e for e in entities if e.entity_type == EntityType.DOMAIN}

        rels = []
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
                        observed_at=datetime.now(timezone.utc),
                    ))
            except Exception:
                pass
        return rels

    def _certificate_issued_to_domain(self, entities: List[Entity]) -> List[Relationship]:
        """Certificate issued to domain."""
        certs = [e for e in entities if e.entity_type == EntityType.CERTIFICATE]
        domains = {e.value: e for e in entities if e.entity_type == EntityType.DOMAIN}

        rels = []
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
                        observed_at=datetime.now(timezone.utc),
                    ))
        return rels

    def _possible_username_match(self, entities: List[Entity]) -> List[Relationship]:
        """Possible username match across platforms."""
        usernames = [e for e in entities if e.entity_type == EntityType.USERNAME]

        rels = []
        for i, u1 in enumerate(usernames):
            for u2 in usernames[i+1:]:
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
                            observed_at=datetime.now(timezone.utc),
                            metadata={"note": "Same username on different platforms - not confirmed same person"},
                        ))
        return rels


class BaseCollector:
    """Base class for all collectors."""

    name: str = "base"
    description: str = "Base collector"
    target_types: List[TargetType] = []

    async def collect(self, context: CollectorContext) -> CollectorResult:
        """Collect intelligence for target."""
        raise NotImplementedError

    def validate_target(self, target: Target) -> bool:
        """Validate target is supported."""
        return target.target_type in self.target_types

    def get_rate_limit_config(self) -> Dict[str, int]:
        """Get rate limit configuration."""
        return {"requests_per_minute": 60}