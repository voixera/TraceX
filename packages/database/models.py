"""TraceX database models."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    Index,
    JSON,
    Integer,
    Float,
    Boolean,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum
import uuid


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class TargetType(str, enum.Enum):
    USERNAME = "username"
    DOMAIN = "domain"
    URL = "url"
    GITHUB = "github"
    IP = "ip"
    EMAIL = "email"


class EntityType(str, enum.Enum):
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


class RelationshipType(str, enum.Enum):
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


class SourceType(str, enum.Enum):
    API = "api"
    DNS = "dns"
    HTTP = "http"
    HTML = "html"
    CERTIFICATE = "certificate"
    WHOIS = "whois"
    USER_INPUT = "user_input"
    PLUGIN = "plugin"


class CaseStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class InvestigationStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


def gen_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    cases: Mapped[List["Case"]] = relationship("Case", back_populates="owner")
    api_keys: Mapped[List["APIKey"]] = relationship("APIKey", back_populates="user")


class APIKey(Base):
    """API key for programmatic access."""

    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(8), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    scopes: Mapped[List[str]] = mapped_column(JSON, default=list)

    user: Mapped["User"] = relationship("User", back_populates="api_keys")

    __table_args__ = (
        Index("ix_api_keys_user_id", "user_id"),
    )


class Case(Base):
    """Investigation case."""

    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[CaseStatus] = mapped_column(
        SQLEnum(CaseStatus), default=CaseStatus.ACTIVE, nullable=False
    )
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    owner: Mapped["User"] = relationship("User", back_populates="cases")
    targets: Mapped[List["Target"]] = relationship("Target", back_populates="case")
    entities: Mapped[List["Entity"]] = relationship("Entity", back_populates="case")
    investigations: Mapped[List["Investigation"]] = relationship("Investigation", back_populates="case")
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="case")
    evidence: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="case")
    relationships: Mapped[List["Relationship"]] = relationship("Relationship", back_populates="case")

    __table_args__ = (
        Index("ix_cases_owner_id", "owner_id"),
        Index("ix_cases_status", "status"),
    )


class Target(Base):
    """Investigation target."""

    __tablename__ = "targets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), nullable=False)
    target_type: Mapped[TargetType] = mapped_column(SQLEnum(TargetType), nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    case: Mapped["Case"] = relationship("Case", back_populates="targets")
    investigations: Mapped[List["Investigation"]] = relationship("Investigation", secondary="investigation_targets", back_populates="targets")

    __table_args__ = (
        Index("ix_targets_case_id", "case_id"),
        Index("ix_targets_type_value", "target_type", "value"),
    )


class Entity(Base):
    """Intelligence graph entity."""

    __tablename__ = "entities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), nullable=False)
    entity_type: Mapped[EntityType] = mapped_column(SQLEnum(EntityType), nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source_ids: Mapped[List[str]] = mapped_column(JSON, default=list)

    case: Mapped["Case"] = relationship("Case", back_populates="entities")
    source_relationships: Mapped[List["Relationship"]] = relationship(
        "Relationship", foreign_keys="Relationship.source_id", back_populates="source_entity"
    )
    target_relationships: Mapped[List["Relationship"]] = relationship(
        "Relationship", foreign_keys="Relationship.target_id", back_populates="target_entity"
    )
    evidence: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="entity")

    __table_args__ = (
        Index("ix_entities_case_id", "case_id"),
        Index("ix_entities_type_value", "entity_type", "value"),
        Index("ix_entities_case_type", "case_id", "entity_type"),
    )


class Relationship(Base):
    """Relationship between entities."""

    __tablename__ = "relationships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), nullable=False)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id"), nullable=False)
    target_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id"), nullable=False)
    relationship_type: Mapped[RelationshipType] = mapped_column(SQLEnum(RelationshipType), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    evidence_ids: Mapped[List[str]] = mapped_column(JSON, default=list)
    source_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    case: Mapped["Case"] = relationship("Case", back_populates="relationships")
    source_entity: Mapped["Entity"] = relationship("Entity", foreign_keys=[source_id], back_populates="source_relationships")
    target_entity: Mapped["Entity"] = relationship("Entity", foreign_keys=[target_id], back_populates="target_relationships")

    __table_args__ = (
        Index("ix_relationships_case_id", "case_id"),
        Index("ix_relationships_source", "source_id"),
        Index("ix_relationships_target", "target_id"),
        Index("ix_relationships_type", "relationship_type"),
    )


class Evidence(Base):
    """Observed evidence."""

    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), nullable=False)
    entity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("entities.id"), nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(SQLEnum(SourceType), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    collector: Mapped[str] = mapped_column(String(100), nullable=False)
    observation: Mapped[str] = mapped_column(Text, nullable=False)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict)
    hash: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    case: Mapped["Case"] = relationship("Case", back_populates="evidence")
    entity: Mapped[Optional["Entity"]] = relationship("Entity", back_populates="evidence")

    __table_args__ = (
        Index("ix_evidence_case_id", "case_id"),
        Index("ix_evidence_entity_id", "entity_id"),
        Index("ix_evidence_collector", "collector"),
        Index("ix_evidence_hash", "hash"),
    )


class Source(Base):
    """Data source configuration."""

    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    source_type: Mapped[SourceType] = mapped_column(SQLEnum(SourceType), nullable=False)
    base_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    api_endpoint: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    rate_limit: Mapped[dict] = mapped_column(JSON, default=dict)
    requires_auth: Mapped[bool] = mapped_column(Boolean, default=False)
    auth_config: Mapped[dict] = mapped_column(JSON, default=dict)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Investigation(Base):
    """Background investigation job."""

    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), nullable=False)
    status: Mapped[InvestigationStatus] = mapped_column(
        SQLEnum(InvestigationStatus), default=InvestigationStatus.PENDING, nullable=False
    )
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    current_collector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    collectors_run: Mapped[List[str]] = mapped_column(JSON, default=list)
    collectors_failed: Mapped[List[str]] = mapped_column(JSON, default=list)
    entities_found: Mapped[int] = mapped_column(Integer, default=0)
    relationships_found: Mapped[int] = mapped_column(Integer, default=0)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[List[dict]] = mapped_column(JSON, default=list)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped["Case"] = relationship("Case", back_populates="investigations")
    targets: Mapped[List["Target"]] = relationship("Target", secondary="investigation_targets", back_populates="investigations")

    __table_args__ = (
        Index("ix_investigations_case_id", "case_id"),
        Index("ix_investigations_status", "status"),
    )


class InvestigationTarget(Base):
    """Association table for investigation targets."""

    __tablename__ = "investigation_targets"

    investigation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("investigations.id"), primary_key=True
    )
    target_id: Mapped[str] = mapped_column(String(36), ForeignKey("targets.id"), primary_key=True)


class Report(Base):
    """Generated report."""

    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[dict] = mapped_column(JSON, default=dict)
    generated_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped["Case"] = relationship("Case", back_populates="reports")

    __table_args__ = (
        Index("ix_reports_case_id", "case_id"),
    )


class AuditLog(Base):
    """Audit log for security and compliance."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
        Index("ix_audit_logs_created_at", "created_at"),
    )


class PluginConfig(Base):
    """Plugin configuration."""

    __tablename__ = "plugin_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    plugin_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Job(Base):
    """Background job queue."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    priority: Mapped[int] = mapped_column(Integer, default=0)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_jobs_status", "status"),
        Index("ix_jobs_scheduled_at", "scheduled_at"),
    )