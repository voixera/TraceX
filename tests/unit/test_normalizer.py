"""Tests for TraceX normalizer."""

from packages.core.normalizer import Normalizer
from packages.models.schemas import EntityType, SourceType


class TestNormalizer:
    """Test normalizer class."""

    def setup_method(self):
        self.normalizer = Normalizer()

    def test_normalize_entity(self):
        raw = {
            "entity_type": "domain",
            "value": "example.com",
            "name": "Example",
            "description": "Test domain",
            "confidence": 0.9,
            "metadata": {"key": "value"},
        }
        entity = self.normalizer.normalize_entity(raw, "test_source")

        assert entity.entity_type == EntityType.DOMAIN
        assert entity.value == "example.com"
        assert entity.name == "Example"
        assert entity.confidence == 0.9
        assert entity.metadata["key"] == "value"
        assert entity.metadata["source"] == "test_source"

    def test_normalize_entity_with_defaults(self):
        raw = {"value": "test.com"}
        entity = self.normalizer.normalize_entity(raw, "src")

        assert entity.entity_type == EntityType.DOMAIN
        assert entity.value == "test.com"
        assert entity.confidence == 1.0

    def test_normalize_evidence(self):
        raw = {
            "observation": "Test observation",
            "raw_data": {"data": "value"},
            "url": "https://example.com",
            "source_type": "dns",
            "confidence": 0.95,
        }
        evidence = self.normalizer.normalize_evidence(
            raw, "src", "collector", entity_id="ent_123", case_id="case_123"
        )

        assert evidence.observation == "Test observation"
        assert evidence.url == "https://example.com"
        assert evidence.source_type == SourceType.DNS
        assert evidence.confidence == 0.95
        assert evidence.entity_id == "ent_123"
        assert evidence.case_id == "case_123"
        assert len(evidence.hash) == 64

    def test_normalize_evidence_invalid_source_type(self):
        raw = {
            "observation": "Test",
            "raw_data": {},
            "source_type": "invalid_type",
        }
        evidence = self.normalizer.normalize_evidence(raw, "src", "collector")

        assert evidence.source_type == SourceType.API

    def test_deduplicate_entities(self):
        from packages.models.schemas import Entity

        entities = [
            Entity(
                id="1",
                entity_type=EntityType.DOMAIN,
                value="example.com",
                confidence=0.9,
                source_ids=["a"],
            ),
            Entity(
                id="2",
                entity_type=EntityType.DOMAIN,
                value="EXAMPLE.COM",
                confidence=1.0,
                source_ids=["b"],
            ),
            Entity(
                id="3",
                entity_type=EntityType.DOMAIN,
                value="other.com",
                confidence=0.8,
                source_ids=["c"],
            ),
        ]

        result = self.normalizer.deduplicate_entities(entities)

        assert len(result) == 2
        for entity in result:
            if entity.value == "example.com":
                assert entity.confidence == 1.0
                assert "a" in entity.source_ids
                assert "b" in entity.source_ids

    def test_normalize_domain_data(self):
        data = {
            "dns": {
                "a": ["1.1.1.1"],
                "mx": [{"value": "mail.com", "preference": 10}],
            },
            "tls": {
                "issuer": "Let's Encrypt",
                "valid_to": "2026-12-31",
            },
            "http": {
                "status_code": 200,
                "headers": {"Server": "nginx"},
            },
        }
        normalized = self.normalizer.normalize_domain_data(data)

        assert "dns" in normalized
        assert normalized["dns"]["a"] == ["1.1.1.1"]
        assert normalized["tls"]["issuer"] == "Let's Encrypt"
        assert normalized["http"]["status_code"] == 200
