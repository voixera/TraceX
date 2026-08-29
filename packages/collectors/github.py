"""GitHub collector - repository and account intelligence."""

import asyncio
import hashlib
import base64
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import httpx

from packages.collectors.base import BaseCollector, CollectorContext
from packages.models.schemas import TargetType, EntityType, SourceType
from packages.common.utils import validate_github_repo, parse_github_url

logger = logging.getLogger(__name__)


class GitHubCollector(BaseCollector):
    """Collect publicly available GitHub intelligence."""

    name = "github"
    description = "Collect GitHub repository and account metadata"
    target_types = [TargetType.GITHUB]
    timeout = 30
    rate_limit = {"requests_per_minute": 30}

    async def _collect_impl(self, context: CollectorContext) -> Dict[str, Any]:
        """Collect GitHub intelligence."""
        target = context.target.value
        repo_name = None

        # Parse target - could be owner/repo or URL
        if target.startswith("http"):
            repo_name = parse_github_url(target)
        else:
            repo_name = target

        if not repo_name or "/" not in repo_name:
            return {"errors": ["Invalid GitHub repository format. Expected owner/repo."]}

        owner, repo = repo_name.split("/", 1)

        entities: List[Any] = []
        relationships: List[Any] = []
        evidence: List[Any] = []
        errors: List[str] = []

        token = self.get_config_value("github_token")
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"
            headers["X-GitHub-Api-Version"] = "2022-11-28"

        async with httpx.AsyncClient(timeout=15) as client:
            # Repository info
            try:
                repo_response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}",
                    headers=headers,
                )
                if repo_response.status_code == 200:
                    repo_data = repo_response.json()

                    # Create repository entity
                    repo_entity = self.create_entity(
                        EntityType.REPOSITORY,
                        f"{owner}/{repo}",
                        name=repo_data.get("full_name", f"{owner}/{repo}"),
                        confidence=1.0,
                        metadata={
                            "description": repo_data.get("description"),
                            "language": repo_data.get("language"),
                            "stargazers_count": repo_data.get("stargazers_count", 0),
                            "forks_count": repo_data.get("forks_count", 0),
                            "open_issues_count": repo_data.get("open_issues_count", 0),
                            "created_at": repo_data.get("created_at"),
                            "updated_at": repo_data.get("updated_at"),
                            "default_branch": repo_data.get("default_branch"),
                            "license": repo_data.get("license", {}).get("spdx_id") if repo_data.get("license") else None,
                            "topics": repo_data.get("topics", []),
                            "visibility": repo_data.get("visibility"),
                            "owner": owner,
                        },
                    )
                    entities.append(repo_entity)

                    evidence.append(self.create_evidence(
                        context=context,
                        observation=f"Repository info for {owner}/{repo}",
                        raw_data={
                            "url": repo_data.get("html_url"),
                            "description": repo_data.get("description"),
                            "language": repo_data.get("language"),
                            "stars": repo_data.get("stargazers_count", 0),
                            "forks": repo_data.get("forks_count", 0),
                            "issues": repo_data.get("open_issues_count", 0),
                        },
                        entity_id=repo_entity.id,
                        confidence=1.0,
                        source_type=SourceType.API,
                    ))

                    # Check if owner has username entity
                    owner_entity = self.create_entity(
                        EntityType.USERNAME,
                        owner,
                        name=owner,
                        confidence=1.0,
                        metadata={
                            "source": "github",
                            "type": repo_data.get("owner", {}).get("type", "User"),
                            "profile_url": repo_data.get("owner", {}).get("html_url"),
                        },
                    )
                    entities.append(owner_entity)

                    # Create relationship: owner owns repo
                    relationships.append({
                        "source_id": owner_entity.id,
                        "target_id": repo_entity.id,
                        "relationship_type": "owns",
                        "confidence": 1.0,
                        "source_reference": "github_api",
                    })

                elif repo_response.status_code == 404:
                    errors.append(f"Repository {owner}/{repo} not found or is private")
                else:
                    errors.append(f"GitHub API returned {repo_response.status_code}")

            except Exception as e:
                errors.append(f"Repository fetch failed: {e}")

            # Contributors
            try:
                contrib_response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/contributors",
                    headers=headers,
                )
                if contrib_response.status_code == 200:
                    contributors = contrib_response.json()

                    for contrib in contributors[:20]:  # Limit to top 20
                        contrib_entity = self.create_entity(
                            EntityType.USERNAME,
                            contrib.get("login", ""),
                            name=contrib.get("login", ""),
                            confidence=0.9,
                            metadata={
                                "source": "github",
                                "contributions": contrib.get("contributions", 0),
                                "type": "contributor",
                            },
                        )
                        entities.append(contrib_entity)

                        evidence.append(self.create_evidence(
                            context=context,
                            observation=f"Contributor to {owner}/{repo}: {contrib.get('login')}",
                            raw_data={
                                "repository": f"{owner}/{repo}",
                                "login": contrib.get("login"),
                                "contributions": contrib.get("contributions", 0),
                            },
                            entity_id=contrib_entity.id,
                            confidence=0.9,
                            source_type=SourceType.API,
                        ))
                elif contrib_response.status_code == 403:
                    self.log.debug("GitHub API rate limit hit for contributors")

            except Exception as e:
                errors.append(f"Contributors fetch failed: {e}")

            # Issues (public)
            try:
                issues_response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=30",
                    headers=headers,
                )
                if issues_response.status_code == 200:
                    issues = issues_response.json()
                    public_issues = [i for i in issues if not i.get("pull_request")]

                    evidence.append(self.create_evidence(
                        context=context,
                        observation=f"Repository has {len(public_issues)} public issues",
                        raw_data={
                            "repository": f"{owner}/{repo}",
                            "issue_count": len(public_issues),
                            "recent_issues": [
                                {"number": i.get("number"), "title": i.get("title"), "state": i.get("state")}
                                for i in public_issues[:10]
                            ],
                        },
                        confidence=0.9,
                        source_type=SourceType.API,
                    ))

            except Exception as e:
                errors.append(f"Issues fetch failed: {e}")

            # Pull requests (public)
            try:
                pr_response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&per_page=30",
                    headers=headers,
                )
                if pr_response.status_code == 200:
                    prs = pr_response.json()

                    evidence.append(self.create_evidence(
                        context=context,
                        observation=f"Repository has {len(prs)} public pull requests",
                        raw_data={
                            "repository": f"{owner}/{repo}",
                            "pr_count": len(prs),
                            "recent_prs": [
                                {"number": p.get("number"), "title": p.get("title"), "state": p.get("state")}
                                for p in prs[:10]
                            ],
                        },
                        confidence=0.9,
                        source_type=SourceType.API,
                    ))

            except Exception as e:
                errors.append(f"Pull requests fetch failed: {e}")

            # Releases
            try:
                releases_response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/releases?per_page=10",
                    headers=headers,
                )
                if releases_response.status_code == 200:
                    releases = releases_response.json()

                    evidence.append(self.create_evidence(
                        context=context,
                        observation=f"Repository has {len(releases)} releases",
                        raw_data={
                            "repository": f"{owner}/{repo}",
                            "release_count": len(releases),
                            "recent_releases": [
                                {"tag": r.get("tag_name"), "name": r.get("name"), "published_at": r.get("published_at")}
                                for r in releases[:5]
                            ],
                        },
                        confidence=0.9,
                        source_type=SourceType.API,
                    ))

            except Exception as e:
                errors.append(f"Releases fetch failed: {e}")

            # Repository topics
            try:
                topics_response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/topics",
                    headers=headers,
                )
                if topics_response.status_code == 200:
                    topics_data = topics_response.json()
                    repo_entity.metadata["topics"] = topics_data.get("names", [])

                    evidence.append(self.create_evidence(
                        context=context,
                        observation=f"Repository topics: {', '.join(topics_data.get('names', []))}",
                        raw_data={
                            "repository": f"{owner}/{repo}",
                            "topics": topics_data.get("names", []),
                        },
                        confidence=0.9,
                        source_type=SourceType.API,
                    ))

            except Exception as e:
                errors.append(f"Topics fetch failed: {e}")

        return {
            "entities": entities,
            "relationships": relationships,
            "evidence": evidence,
            "errors": errors,
        }