"""Username collector - check public profiles across platforms."""

import asyncio
import logging
from typing import Any

import httpx

from packages.collectors.base import BaseCollector, CollectorContext
from packages.models.schemas import EntityType, SourceType, TargetType

logger = logging.getLogger(__name__)


class UsernameCollector(BaseCollector):
    """Check username existence on public platforms."""

    name = "username"
    description = "Check username existence on public platforms"
    target_types = [TargetType.USERNAME]
    timeout = 30

    PLATFORMS: dict[str, dict[str, Any]] = {
        "github": {
            "url": "https://github.com/{username}",
            "method": "GET",
            "status_code": 200,
        },
        "gitlab": {
            "url": "https://gitlab.com/{username}",
            "method": "GET",
            "status_code": 200,
        },
        "reddit": {
            "url": "https://www.reddit.com/user/{username}",
            "method": "GET",
            "status_code": 200,
        },
    }

    async def _collect_impl(self, context: CollectorContext) -> dict[str, Any]:
        """Check username across platforms."""
        username = context.target.value

        entities: list[Any] = []
        relationships: list[Any] = []
        evidence: list[Any] = []
        errors: list[str] = []

        async with httpx.AsyncClient(timeout=10) as client:
            for platform, config in self.PLATFORMS.items():
                try:
                    url = config["url"].format(username=username)
                    response = await client.get(
                        url,
                        headers={
                            "User-Agent": "TraceX-OSINT/0.1.0 (research project)",
                            "Accept": "text/html,application/xhtml+xml",
                        },
                        follow_redirects=True,
                    )

                    found = response.status_code == config["status_code"]
                    confidence = 0.8 if found else 0.1

                    entity = self.create_entity(
                        EntityType.USERNAME,
                        username,
                        name=f"{username} on {platform}",
                        confidence=confidence,
                        metadata={
                            "source": f"{platform}_profile",
                            "platform": platform,
                            "found": found,
                            "status_code": response.status_code,
                            "url": url,
                        },
                    )
                    entities.append(entity)

                    evidence.append(self.create_evidence(
                        context=context,
                        observation=f"Username '{username}' {'found' if found else 'not found'} on {platform}",
                        raw_data={
                            "platform": platform,
                            "username": username,
                            "found": found,
                            "status_code": response.status_code,
                            "url": url,
                        },
                        entity_id=entity.id,
                        confidence=confidence,
                        source_type=SourceType.HTML,
                    ))

                    await asyncio.sleep(0.3)

                except Exception as e:
                    errors.append(f"{platform} check failed: {e}")
                    self.log.debug(f"{platform} check failed for {username}: {e}")

        return {
            "entities": entities,
            "relationships": relationships,
            "evidence": evidence,
            "errors": errors,
        }
