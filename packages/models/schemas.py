"""TraceX Pydantic models and schemas."""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, EmailStr, validator
import uuid


class TargetType(str, Enum):
    """Supported investigation target types."""

    USERNAME = "username"
    DOMAIN = "domain"
    URL = "url"
    GITHUB = "github"
    IP = "ip"
    EMAIL = "email"


class EntityType(str, Enum):
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


class RelationshipType(str, Enum):
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


class ConfidenceLevel(str, Enum):
    """Confidence levels for findings."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"


class SourceType(str, Enum):
    """Data source types."""

    API = "api"
    DNS = "dns"
    HTTP = "http"
    HTML = "html"
    CERTIFICATE = "certificate"
    WHOIS = "whois"
    USER_INPUT = "user_input"
    PLUGIN = "plugin"


class CaseStatus(str, Enum):
    """Investigation case status."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class InvestigationStatus(str, Enum):
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
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class Entity(BaseModel):
    """Intelligence graph entity."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: EntityType
    value: str
    name: Optional[str] = None
    description: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    first_seen: datetime = Field(default_factory=lambda: datetime.now())
    last_seen: datetime = Field(default_factory=lambda: datetime.now())
    source_ids: List[str] = Field(default_factory=list)
    case_ids: List[str] = Field(default_factory=list)


class Relationship(BaseModel):
    """Relationship between entities."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence_ids: List[str] = Field(default_factory=list)
    source_reference: Optional[str] = None
    observed_at: datetime = Field(default_factory=lambda: datetime.now())
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Evidence(BaseModel):
    """Observed evidence."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    entity_id: Optional[str] = None
    source: str
    source_type: SourceType
    url: Optional[str] = None
    collector: str
    observation: str
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    hash: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    observed_at: datetime = Field(default_factory=lambda: datetime.now())
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Source(BaseModel):
    """Data source."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    source_type: SourceType
    base_url: Optional[str] = None
    api_endpoint: Optional[str] = None
    rate_limit: Dict[str, int] = Field(default_factory=dict)
    requires_auth: bool = False
    description: Optional[str] = None
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Case(BaseModel):
    """Investigation case."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    status: CaseStatus = CaseStatus.ACTIVE
    tags: List[str] = Field(default_factory=list)
    target_ids: List[str] = Field(default_factory=list)
    entity_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    archived_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Investigation(BaseModel):
    """Background investigation job."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    target_ids: List[str]
    status: InvestigationStatus = InvestigationStatus.PENDING
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    current_collector: Optional[str] = None
    collectors_run: List[str] = Field(default_factory=list)
    collectors_failed: List[str] = Field(default_factory=list)
    entities_found: int = 0
    relationships_found: int = 0
    evidence_count: int = 0
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class Report(BaseModel):
    """Generated report."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    title: str
    format: str  # json, markdown, html, pdf
    content: str
    summary: Dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=lambda: datetime.now())
    generated_by: Optional[str] = None


class CollectorResult(BaseModel):
    """Result from a collector."""

    collector: str
    target: str
    target_type: TargetType
    success: bool
    entities: List[Entity] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    execution_time: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class APIResponse(BaseModel):
    """Standard API response."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated API response."""

    items: List[Any]
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
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Graph edge for visualization."""

    id: str
    source: str
    target: str
    type: str
    confidence: float
    label: Optional[str] = None


class GraphData(BaseModel):
    """Graph visualization data."""

    nodes: List[GraphNode]
    edges: List[GraphEdge]