"""Tests for TraceX collectors."""

from packages.collectors.base import CollectorContext
from packages.collectors.domain import DomainCollector
from packages.collectors.github import GitHubCollector
from packages.collectors.url import URLCollector
from packages.collectors.username import UsernameCollector
from packages.models.schemas import (
    EntityType,
    Target,
    TargetType,
)


class TestDomainCollector:
    """Test domain collector."""

    def setup_method(self):
        self.collector = DomainCollector()

    def test_collector_attributes(self):
        assert self.collector.name == "domain"
        assert TargetType.DOMAIN in self.collector.target_types

    def test_validate_target(self):
        domain_target = Target(
            case_id="case_1",
            target_type=TargetType.DOMAIN,
            value="example.com",
        )
        url_target = Target(
            case_id="case_1",
            target_type=TargetType.URL,
            value="https://example.com",
        )

        assert self.collector.validate_target(domain_target) is True
        assert self.collector.validate_target(url_target) is False

    def test_create_entity(self):
        entity = self.collector.create_entity(
            entity_type=EntityType.DOMAIN,
            value="example.com",
            confidence=0.9,
        )

        assert entity.value == "example.com"
        assert entity.entity_type == EntityType.DOMAIN
        assert entity.confidence == 0.9
        assert entity.metadata["source"] == "domain"

    def test_create_evidence(self):
        target = Target(
            case_id="case_1",
            target_type=TargetType.DOMAIN,
            value="example.com",
        )
        context = CollectorContext(
            case_id="case_1",
            target=target,
            config={},
        )

        evidence = self.collector.create_evidence(
            context=context,
            observation="Test observation",
            raw_data={"test": "data"},
            confidence=1.0,
        )

        assert evidence.observation == "Test observation"
        assert evidence.case_id == "case_1"
        assert evidence.source == "domain"
        assert evidence.confidence == 1.0


class TestURLCollector:
    """Test URL collector."""

    def setup_method(self):
        self.collector = URLCollector()

    def test_collector_attributes(self):
        assert self.collector.name == "url"
        assert TargetType.URL in self.collector.target_types


class TestGitHubCollector:
    """Test GitHub collector."""

    def setup_method(self):
        self.collector = GitHubCollector()

    def test_collector_attributes(self):
        assert self.collector.name == "github"
        assert TargetType.GITHUB in self.collector.target_types


class TestUsernameCollector:
    """Test username collector."""

    def setup_method(self):
        self.collector = UsernameCollector()

    def test_collector_attributes(self):
        assert self.collector.name == "username"
        assert TargetType.USERNAME in self.collector.target_types
        assert len(self.collector.PLATFORMS) > 0


class TestBaseCollector:
    """Test base collector functionality."""

    def test_collector_context_creation(self):
        target = Target(
            case_id="case_1",
            target_type=TargetType.DOMAIN,
            value="example.com",
        )
        context = CollectorContext(
            case_id="case_1",
            target=target,
            config={},
        )

        assert context.case_id == "case_1"
        assert context.target == target
        assert context.config == {}

    def test_get_config_value(self):
        collector = DomainCollector({"key": "value"})
        assert collector.get_config_value("key") == "value"
        assert collector.get_config_value("missing", "default") == "default"
        assert collector.get_config_value("missing") is None
