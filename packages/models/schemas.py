"""TraceX Pydantic models and schemas."""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class TargetType(StrEnum):
    """Supported investigation target types."""

    USERNAME = "username"
    DOMAIN = "domain"
    URL = "url"
    GITHUB = "github"
    IP = "ip"
    EMAIL = "email"


class EntityType(StrEnum):
    """Entity types in the intelligence graph."""

    USERNAME = "username"
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    URL = "url"
    IP = "ip"
    ASN = "asn"
    ORGANIZATION = "organization"
    REPOSITORY = "repository"
    EMAIL = "email"
    CERTIFICATE = "certificate"
    TECHNOLOGY = "technology"
    PERSON = "person"


class RelationshipType(StrEnum):
    """Relationship types between entities."""

    OWNS = "owns"
    MAINTAINS = "maintains"
    HOSTS = "hosts"
    RESOLVES_TO = "resolves_to"
    CONTAINS = "contains"
    REFERENCES = "references"
    USES_TECHNOLOGY = "uses_technology"
    ASSOCIATED_WITH = "associated_with"
    POSSIBLE_MATCH = "possible_match"
    SAME_AS = "same_as"


class ConfidenceLevel(StrEnum):
    """Confidence levels for findings."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"


class SourceType(StrEnum):
    """Data source types."""

    API = "api"
    DNS = "dns"
    HTTP = "http"
    HTML = "html"
    CERTIFICATE = "certificate"
    WHOIS = "whois"
    USER_INPUT = "user_input"
    PLUGIN = "plugin"


class CaseStatus(StrEnum):
    """Investigation case status."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class InvestigationStatus(StrEnum):
    """Investigation job status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class Target(BaseModel):
    """Investigation target."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    target_type: TargetType
    value: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class Entity(BaseModel):
    """Intelligence graph entity."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: EntityType
    value: str
    name: str | None = None
    description: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    first_seen: datetime = Field(default_factory=lambda: datetime.now())
    last_seen: datetime = Field(default_factory=lambda: datetime.now())
    source_ids: list[str] = Field(default_factory=list)
    case_ids: list[str] = Field(default_factory=list)


class Relationship(BaseModel):
    """Relationship between entities."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list)
    source_reference: str | None = None
    observed_at: datetime = Field(default_factory=lambda: datetime.now())
    metadata: dict[str, Any] = Field(default_factory=dict)


class Evidence(BaseModel):
    """Observed evidence."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    entity_id: str | None = None
    source: str
    source_type: SourceType
    url: str | None = None
    collector: str
    observation: str
    raw_data: dict[str, Any] = Field(default_factory=dict)
    hash: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    observed_at: datetime = Field(default_factory=lambda: datetime.now())
    metadata: dict[str, Any] = Field(default_factory=dict)


class Source(BaseModel):
    """Data source."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    source_type: SourceType
    base_url: str | None = None
    api_endpoint: str | None = None
    rate_limit: dict[str, int] = Field(default_factory=dict)
    requires_auth: bool = False
    description: str | None = None
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class Case(BaseModel):
    """Investigation case."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str | None = None
    status: CaseStatus = CaseStatus.ACTIVE
    tags: list[str] = Field(default_factory=list)
    target_ids: list[str] = Field(default_factory=list)
    entity_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    archived_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Investigation(BaseModel):
    """Background investigation job."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    target_ids: list[str]
    status: InvestigationStatus = InvestigationStatus.PENDING
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    current_collector: str | None = None
    collectors_run: list[str] = Field(default_factory=list)
    collectors_failed: list[str] = Field(default_factory=list)
    entities_found: int = 0
    relationships_found: int = 0
    evidence_count: int = 0
    errors: list[dict[str, Any]] = Field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class Report(BaseModel):
    """Generated report."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    title: str
    format: str  # json, markdown, html, pdf
    content: str
    summary: dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=lambda: datetime.now())
    generated_by: str | None = None


class CollectorResult(BaseModel):
    """Result from a collector."""

    collector: str
    target: str
    target_type: TargetType
    success: bool
    entities: list[Entity] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    execution_time: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class APIResponse(BaseModel):
    """Standard API response."""

    success: bool
    data: Any | None = None
    error: str | None = None
    message: str | None = None


class PaginatedResponse(BaseModel):
    """Paginated API response."""

    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class GraphNode(BaseModel):
    """Graph node for visualization."""

    id: str
    label: str
    type: str
    confidence: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Graph edge for visualization."""

    id: str
    source: str
    target: str
    type: str
    confidence: float
    label: str | None = None


class GraphData(BaseModel):
    """Graph visualization data."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]
