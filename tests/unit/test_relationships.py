"""Tests for TraceX relationships engine."""

from packages.core.relationships import RelationshipEngine
from packages.models.schemas import (
    Entity,
    EntityType,
    RelationshipType,
)


class TestRelationshipEngine:
    """Test relationship inference engine."""

    def setup_method(self):
        self.engine = RelationshipEngine()

    def test_infer_relationships_empty(self):
        relationships = self.engine.infer_relationships([])
        assert relationships == []

    def test_github_owns_repo_relationship(self):
        entities = [
            Entity(
                id="user_1",
                entity_type=EntityType.USERNAME,
                value="octocat",
                metadata={"source": "github", "owner": "octocat"},
            ),
            Entity(
                id="repo_1",
                entity_type=EntityType.REPOSITORY,
                value="hello-world",
                metadata={"owner": "octocat"},
            ),
        ]

        relationships = self.engine._github_owns_repo(entities)

        assert len(relationships) == 1
        assert relationships[0].source_id == "user_1"
        assert relationships[0].target_id == "repo_1"
        assert relationships[0].relationship_type == RelationshipType.OWNS
        assert relationships[0].confidence == 1.0

    def test_domain_has_subdomain_relationship(self):
        entities = [
            Entity(
                id="domain_1",
                entity_type=EntityType.DOMAIN,
                value="example.com",
            ),
            Entity(
                id="sub_1",
                entity_type=EntityType.SUBDOMAIN,
                value="api.example.com",
            ),
        ]

        relationships = self.engine._domain_has_subdomain(entities)

        assert len(relationships) == 1
        assert relationships[0].source_id == "domain_1"
        assert relationships[0].target_id == "sub_1"
        assert relationships[0].relationship_type == RelationshipType.HOSTS

    def test_url_belongs_to_domain(self):
        entities = [
            Entity(
                id="domain_1",
                entity_type=EntityType.DOMAIN,
                value="example.com",
            ),
            Entity(
                id="url_1",
                entity_type=EntityType.URL,
                value="https://example.com/page",
            ),
        ]

        relationships = self.engine._url_belongs_to_domain(entities)

        assert len(relationships) == 1
        assert relationships[0].source_id == "domain_1"
        assert relationships[0].target_id == "url_1"

    def test_possible_username_match(self):
        entities = [
            Entity(
                id="u1",
                entity_type=EntityType.USERNAME,
                value="john",
                metadata={"source": "github"},
            ),
            Entity(
                id="u2",
                entity_type=EntityType.USERNAME,
                value="JOHN",
                metadata={"source": "reddit"},
            ),
        ]

        relationships = self.engine._possible_username_match(entities)

        assert len(relationships) == 1
        assert relationships[0].relationship_type == RelationshipType.POSSIBLE_MATCH
        assert relationships[0].confidence == 0.7

    def test_infer_relationships_combined(self):
        entities = [
            Entity(
                id="user_1",
                entity_type=EntityType.USERNAME,
                value="octocat",
                metadata={"source": "github"},
            ),
            Entity(
                id="repo_1",
                entity_type=EntityType.REPOSITORY,
                value="hello-world",
                metadata={"owner": "octocat"},
            ),
            Entity(
                id="domain_1",
                entity_type=EntityType.DOMAIN,
                value="example.com",
            ),
            Entity(
                id="url_1",
                entity_type=EntityType.URL,
                value="https://example.com",
            ),
        ]

        relationships = self.engine.infer_relationships(entities)

        assert len(relationships) >= 2
        rel_types = [r.relationship_type for r in relationships]
        assert RelationshipType.OWNS in rel_types
        assert RelationshipType.HOSTS in rel_types
