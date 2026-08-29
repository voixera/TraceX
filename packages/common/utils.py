"""TraceX common utilities."""

import hashlib
import ipaddress
import re
import secrets
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse


def generate_id(prefix: str = "") -> str:
    """Generate unique ID with optional prefix."""
    suffix = secrets.token_hex(8)
    return f"{prefix}{suffix}" if prefix else suffix


def hash_evidence(data: str) -> str:
    """Generate SHA-256 hash for evidence."""
    return hashlib.sha256(data.encode()).hexdigest()


def validate_domain(domain: str) -> bool:
    """Validate domain format."""
    pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    return bool(re.match(pattern, domain))


def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except ValueError:
        return False


def validate_ip(ip: str) -> bool:
    """Validate IP address (IPv4 or IPv6)."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def validate_github_repo(repo: str) -> bool:
    """Validate GitHub repository format (owner/repo)."""
    pattern = r"^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$"
    return bool(re.match(pattern, repo))


def parse_github_url(url: str) -> str | None:
    """Extract owner/repo from GitHub URL."""
    patterns = [
        r"github\.com/([^/]+)/([^/\s]+)",
        r"github\.com/([^/]+)/([^/\s]+)/tree/[^/]+/([^/\s]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
    return None


def normalize_domain(domain: str) -> str:
    """Normalize domain (lowercase, remove trailing dot)."""
    domain = domain.lower().strip()
    return domain.rstrip(".")


def extract_subdomains(domain: str) -> list[str]:
    """Extract subdomains from domain."""
    parts = domain.split(".")
    if len(parts) > 2:
        return [".".join(parts[i:]) for i in range(len(parts) - 1)]
    return []


def get_current_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(UTC).isoformat()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem usage."""
    return re.sub(r"[^\w\s.-]", "", filename)[:255]


def mask_sensitive(text: str, visible_chars: int = 4) -> str:
    """Mask sensitive information, showing only last N characters."""
    if len(text) <= visible_chars:
        return "*" * len(text)
    return "*" * (len(text) - visible_chars) + text[-visible_chars:]


def parse_tags(tags: str) -> list[str]:
    """Parse comma/space separated tags."""
    return [t.strip().lower() for t in re.split(r"[,\s]+", tags) if t.strip()]


def format_bytes(num_bytes: int) -> str:
    """Format bytes to human readable."""
    size: float = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def calculate_confidence_factors(evidence_count: int, source_count: int, cross_reference: int) -> float:
    """Calculate confidence score based on evidence factors."""
    if evidence_count == 0:
        return 0.0
    score = min(1.0, evidence_count / 10)
    score += min(0.3, source_count * 0.1)
    score += min(0.2, cross_reference * 0.1)
    return round(min(1.0, score), 2)


def build_evidence_hash(evidence: dict[str, Any]) -> str:
    """Build deterministic hash from evidence data."""
    import json
    canonical = json.dumps(evidence, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
