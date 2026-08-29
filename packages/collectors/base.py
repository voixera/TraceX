"""TraceX base collector class."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from packages.common.utils import generate_id
from packages.models.schemas import (
    Entity,
    EntityType,
    Evidence,
    Relationship,
    SourceType,
    Target,
    TargetType,
)

logger = logging.getLogger(__name__)


@dataclass
class CollectorConfig:
    """Collector configuration."""

    name: str
    description: str = ""
    target_types: list[TargetType] = field(default_factory=list)
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit: dict[str, int] = field(default_factory=lambda: {"requests_per_minute": 60})
    requires_auth: bool = False
    enabled: bool = True


@dataclass
class CollectorResult:
    """Result from collector execution."""

    collector: str
    target: str
    target_type: TargetType
    success: bool
    entities: list[Entity] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CollectorContext:
    """Context passed to collectors during execution."""

    case_id: str
    target: Target
    config: dict[str, Any]
    session: Any | None = None


class BaseCollector(ABC):
    """Base class for all collectors."""

    name: str = "base"
    description: str = "Base collector class"
    target_types: list[TargetType] = []
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit: dict[str, int] | None = None
    requires_auth: bool = False

    def __init__(self, config: dict[str, Any] | None = None):
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

    async def collect(self, context: CollectorContext) -> CollectorResult:
        """Collect intelligence for a target."""
        start_time = datetime.now(UTC)

        if not self.validate_target(context.target):
            return CollectorResult(
                collector=self.name,
                target=context.target.value,
                target_type=context.target.target_type,
                success=False,
                errors=[f"Target type {context.target.target_type} not supported"],
                execution_time=0,
            )

        entities: list[Entity] = []
        relationships: list[Relationship] = []
        evidence: list[Evidence] = []
        errors: list[str] = []

        try:
            result = await self._collect_impl(context)
            if isinstance(result, dict):
                entities = result.get("entities", [])
                relationships = result.get("relationships", [])
                evidence = result.get("evidence", [])
                errors = result.get("errors", [])

        except TimeoutError:
            errors.append(f"Collection timed out after {self.timeout}s")
        except Exception as e:
            errors.append(str(e))
            self.log.error(f"Error collecting from {self.name}: {e}")

        execution_time = (datetime.now(UTC) - start_time).total_seconds()

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
    async def _collect_impl(self, context: CollectorContext) -> dict[str, Any]:
        """Implement collection logic. Must return dict with entities, relationships, evidence, errors."""
        pass

    def create_evidence(
        self,
        context: CollectorContext,
        observation: str,
        raw_data: dict[str, Any],
        entity_id: str | None = None,
        confidence: float = 1.0,
        source_type: SourceType = SourceType.API,
        url: str | None = None,
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
            observed_at=datetime.now(UTC),
        )

    def create_entity(
        self,
        entity_type: EntityType,
        value: str,
        name: str | None = None,
        confidence: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> Entity:
        """Create entity object."""
        meta = metadata or {}
        meta["source"] = self.name

        return Entity(
            id=generate_id(f"ent_{entity_type.value}_"),
            entity_type=entity_type,
            value=value,
            name=name or value,
            confidence=confidence,
            metadata=meta,
            source_ids=[self.name],
        )
