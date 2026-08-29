"""TraceX base collector class."""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from packages.models.schemas import (
    CollectorResult,
    Target,
    Entity,
    Relationship,
    Evidence,
    TargetType,
    EntityType,
    SourceType,
    RelationshipType,
)
from packages.common.utils import generate_id, get_current_timestamp

logger = logging.getLogger(__name__)


@dataclass
class CollectorConfig:
    """Collector configuration."""

    name: str
    description: str = ""
    target_types: List[TargetType] = field(default_factory=list)
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit: Dict[str, int] = field(default_factory=lambda: {"requests_per_minute": 60})
    requires_auth: bool = False
    enabled: bool = True


class BaseCollector(ABC):
    """Base class for all collectors."""

    name: str = "base"
    description: str = "Base collector class"
    target_types: List[TargetType] = []
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit: Dict[str, int] = None
    requires_auth: bool = False

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._session = None
        self._logger = logging.getLogger(f"collectors.{self.name}")

    @property
    def log(self) -> logging.Logger:
        return self._logger

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def validate_target(self, target: Target) -> bool:
        """Validate that target is supported by this collector."""
        return target.target_type in self.target_types

    async def collect(self, context: "CollectorContext") -> CollectorResult:
        """Collect intelligence for a target."""
        start_time = datetime.now(timezone.utc)

        if not self.validate_target(context.target):
            return CollectorResult(
                collector=self.name,
                target=context.target.value,
                target_type=context.target.target_type,
                success=False,
                errors=[f"Target type {context.target.target_type} not supported"],
                execution_time=0,
            )

        entities: List[Entity] = []
        relationships: List[Relationship] = []
        evidence: List[Evidence] = []
        errors: List[str] = []

        try:
            # Execute collection logic
            result = await self._collect_impl(context)

            if isinstance(result, dict):
                entities = result.get("entities", [])
                relationships = result.get("relationships", [])
                evidence = result.get("evidence", [])
                errors = result.get("errors", [])

        except asyncio.TimeoutError:
            errors.append(f"Collection timed out after {self.timeout}s")
        except Exception as e:
            errors.append(str(e))
            self.log.error(f"Error collecting from {self.name}: {e}")

        execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()

        return CollectorResult(
            collector=self.name,
            target=context.target.value,
            target_type=context.target.target_type,
            success=len(errors) == 0,
            entities=entities,
            relationships=relationships,
            evidence=evidence,
            errors=errors,
            execution_time=execution_time,
            metadata=context.target.metadata,
        )

    @abstractmethod
    async def _collect_impl(self, context: "CollectorContext") -> Dict[str, Any]:
        """Implement collection logic. Must return dict with entities, relationships, evidence, errors."""
        pass

    def create_evidence(
        self,
        context: "CollectorContext",
        observation: str,
        raw_data: Dict[str, Any],
        entity_id: Optional[str] = None,
        confidence: float = 1.0,
        source_type: SourceType = SourceType.API,
        url: Optional[str] = None,
    ) -> Evidence:
        """Create evidence object."""
        return Evidence(
            id=generate_id("ev_"),
            case_id=context.case_id,
            entity_id=entity_id,
            source=self.name,
            source_type=source_type,
            url=url,
            collector=self.name,
            observation=observation,
            raw_data=raw_data,
            hash="",
            confidence=confidence,
            observed_at=datetime.now(timezone.utc),
        )

    def create_entity(
        self,
        entity_type: EntityType,
        value: str,
        name: Optional[str] = None,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Entity:
        """Create entity object."""
        from packages.common.utils import build_evidence_hash

        meta = metadata or {}
        meta["source"] = self.name

        data = {
            "entity_type": entity_type.value,
            "value": value,
            "name": name or value,
            "confidence": confidence,
            "metadata": meta,
        }

        return Entity(
            id=generate_id(f"ent_{entity_type.value}_"),
            entity_type=entity_type,
            value=value,
            name=name or value,
            confidence=confidence,
            metadata=meta,
            source_ids=[self.name],
        )


@dataclass
class CollectorContext:
    """Context passed to collectors during execution."""

    case_id: str
    target: Target
    config: Dict[str, Any]
    session: Optional[Any] = None


@dataclass
class CollectorResult:
    """Result from collector execution."""

    collector: str
    target: str
    target_type: TargetType
    success: bool
    entities: List[Entity] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    evidence: List[Evidence] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.entities:
            self.entities = []
        if not self.relationships:
            self.relationships = []
        if not self.evidence:
            self.evidence = []
        if not self.errors:
            self.errors = []