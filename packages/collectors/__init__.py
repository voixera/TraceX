"""TraceX collectors package."""

from .base import BaseCollector, CollectorContext
from .domain import DomainCollector
from .url import URLCollector
from .github import GitHubCollector
from .username import UsernameCollector


__all__ = [
    "BaseCollector",
    "CollectorContext",
    "DomainCollector",
    "URLCollector",
    "GitHubCollector",
    "UsernameCollector",
]


def get_available_collectors() -> dict:
    """Get all available collectors."""
    return {
        "domain": DomainCollector,
        "url": URLCollector,
        "github": GitHubCollector,
        "username": UsernameCollector,
    }


def create_collector(name: str, config: dict = None):
    """Create collector instance by name."""
    collectors = get_available_collectors()
    if name not in collectors:
        raise ValueError(f"Unknown collector: {name}")
    return collectors[name](config)