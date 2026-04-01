"""GitHub source — discovers trending AI repos and tutorial repositories."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ai_tutorial_hunter.config.settings import get_settings
from ai_tutorial_hunter.models.trend import Trend
from ai_tutorial_hunter.models.tutorial import Tutorial
from ai_tutorial_hunter.sources.base import BaseSource


class GitHubSource(BaseSource):
    name = "github"
    base_url = "https://api.github.com"

    async def fetch_trending(self, limit: int = 20) -> list[Trend]:
        """Find trending AI/ML repos created or updated recently."""
        since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
        queries = [
            "AI tutorial",
            "LLM tutorial",
            "machine learning guide",
            "AI agents",
            "RAG tutorial",
        ]
        trends: list[Trend] = []
        for q in queries:
            params = {
                "q": f"{q} created:>{since}",
                "sort": "stars",
                "order": "desc",
                "per_page": min(limit, 10),
            }
            headers = {}
            token = get_settings().github_token
            if token:
                headers["Authorization"] = f"Bearer {token}"

            resp = await self._client.get(
                f"{self.base_url}/search/repositories",
                params=params,
                headers=headers,
            )
            if resp.status_code != 200:
                continue

            data = resp.json()
            for item in data.get("items", []):
                trends.append(
                    Trend(
                        topic=item.get("name", q),
                        query=q,
                        velocity=item.get("stargazers_count", 0) / max(1, 7),
                        volume=item.get("stargazers_count", 0),
                        sources=["github"],
                        category="frameworks",
                        related_topics=[t.get("name", "") for t in item.get("topics", [])[:5]],
                    )
                )
        return trends[:limit]

    async def search_tutorials(self, query: str, limit: int = 20) -> list[Tutorial]:
        """Search GitHub for tutorial repositories."""
        params = {
            "q": f"{query} tutorial OR guide OR course in:name,description,readme",
            "sort": "stars",
            "order": "desc",
            "per_page": min(limit, 30),
        }
        headers = {}
        token = get_settings().github_token
        if token:
            headers["Authorization"] = f"Bearer {token}"

        resp = await self._client.get(
            f"{self.base_url}/search/repositories",
            params=params,
            headers=headers,
        )
        if resp.status_code != 200:
            return []

        data = resp.json()
        tutorials: list[Tutorial] = []
        for item in data.get("items", []):
            published = None
            if item.get("created_at"):
                published = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))

            tutorials.append(
                Tutorial(
                    title=item.get("full_name", ""),
                    url=item.get("html_url", ""),
                    source="github",
                    author=item.get("owner", {}).get("login", ""),
                    published_at=published,
                    topic=query,
                    tags=item.get("topics", [])[:10],
                    content_type="repository",
                    summary=item.get("description", "") or "",
                    engagement={
                        "stars": item.get("stargazers_count", 0),
                        "forks": item.get("forks_count", 0),
                        "watchers": item.get("watchers_count", 0),
                    },
                )
            )
        return tutorials[:limit]
