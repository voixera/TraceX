"""Tests for TraceX common utilities."""

from packages.common.utils import (
    calculate_confidence_factors,
    generate_id,
    hash_evidence,
    normalize_domain,
    validate_domain,
    validate_github_repo,
    validate_ip,
    validate_url,
)


class TestValidation:
    """Test validation functions."""

    def test_validate_domain_valid(self):
        assert validate_domain("example.com") is True
        assert validate_domain("sub.example.com") is True
        assert validate_domain("example.co.uk") is True

    def test_validate_domain_invalid(self):
        assert validate_domain("not a domain") is False
        assert validate_domain("") is False
        assert validate_domain("localhost") is False

    def test_validate_url_valid(self):
        assert validate_url("https://example.com") is True
        assert validate_url("http://sub.example.com/path") is True
        assert validate_url("https://example.com:8080") is True

    def test_validate_url_invalid(self):
        assert validate_url("not a url") is False
        assert validate_url("") is False
        assert validate_url("ftp://example.com") is False

    def test_validate_ip(self):
        assert validate_ip("192.168.1.1") is True
        assert validate_ip("::1") is True
        assert validate_ip("invalid") is False

    def test_validate_github_repo(self):
        assert validate_github_repo("owner/repo") is True
        assert validate_github_repo("user-name/project-name") is True
        assert validate_github_repo("invalid") is False
        assert validate_github_repo("") is False


class TestNormalization:
    """Test normalization functions."""

    def test_normalize_domain(self):
        assert normalize_domain("EXAMPLE.COM") == "example.com"
        assert normalize_domain("Example.Com.") == "example.com"
        assert normalize_domain("  example.com  ") == "example.com"


class TestUtilities:
    """Test utility functions."""

    def test_generate_id(self):
        id1 = generate_id()
        id2 = generate_id()
        assert id1 != id2
        assert len(id1) == 16

    def test_generate_id_with_prefix(self):
        id1 = generate_id("test_")
        assert id1.startswith("test_")
        assert len(id1) > 5

    def test_hash_evidence(self):
        hash1 = hash_evidence("test data")
        hash2 = hash_evidence("test data")
        hash3 = hash_evidence("different data")
        assert hash1 == hash2
        assert hash1 != hash3
        assert len(hash1) == 64

    def test_calculate_confidence_factors(self):
        confidence = calculate_confidence_factors(
            evidence_count=5,
            source_count=3,
            cross_reference=2
        )
        assert 0 <= confidence <= 1.0
        assert isinstance(confidence, float)

    def test_calculate_confidence_zero_evidence(self):
        confidence = calculate_confidence_factors(0, 0, 0)
        assert confidence == 0.0
