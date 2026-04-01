"""Hacker News source — monitors for trending AI discussions and tutorials."""

from __future__ import annotations

from datetime import datetime, timezone

from ai_tutorial_hunter.models.trend import Trend
from ai_tutorial_hunter.models.tutorial import Tutorial
from ai_tutorial_hunter.sources.base import BaseSource

AI_KEYWORDS = [
    "ai", "llm", "gpt", "claude", "machine learning", "deep learning",
    "neural", "transformer", "diffusion", "agent", "rag", "fine-tun",
    "embedding", "vector", "langchain", "hugging face", "openai", "anthropic",
]


class HackerNewsSource(BaseSource):
    name = "hackernews"
    base_url = "https://hacker-news.firebaseio.com/v0"

    async def fetch_trending(self, limit: int = 20) -> list[Trend]:
        """Get top HN stories and filter for AI-related ones."""
        resp = await self._client.get(f"{self.base_url}/topstories.json")
        if resp.status_code != 200:
            return []

        story_ids = resp.json()[:100]
        trends: list[Trend] = []

        for story_id in story_ids:
            if len(trends) >= limit:
                break
            item_resp = await self._client.get(f"{self.base_url}/item/{story_id}.json")
            if item_resp.status_code != 200:
                continue

            item = item_resp.json()
            if not item:
                continue

            title = (item.get("title") or "").lower()
            if not any(kw in title for kw in AI_KEYWORDS):
                continue

            trends.append(
                Trend(
                    topic=item.get("title", "")[:100],
                    query=item.get("title", "")[:100],
                    velocity=item.get("score", 0) / 10,
                    volume=item.get("score", 0),
                    sources=["hackernews"],
                    category="",
                    related_topics=[],
                )
            )
        return trends[:limit]

    async def search_tutorials(self, query: str, limit: int = 20) -> list[Tutorial]:
        """Search HN via Algolia API for tutorial content."""
        resp = await self._client.get(
            "https://hn.algolia.com/api/v1/search",
            params={
                "query": f"{query} tutorial",
                "tags": "story",
                "hitsPerPage": min(limit, 30),
            },
        )
        if resp.status_code != 200:
            return []

        data = resp.json()
        tutorials: list[Tutorial] = []
        for hit in data.get("hits", []):
            created = None
            if hit.get("created_at"):
                try:
                    created = datetime.fromisoformat(
                        hit["created_at"].replace("Z", "+00:00")
                    )
                except ValueError:
                    pass

            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"

            tutorials.append(
                Tutorial(
                    title=hit.get("title", ""),
                    url=url,
                    source="hackernews",
                    author=hit.get("author", ""),
                    published_at=created,
                    topic=query,
                    content_type="article",
                    summary="",
                    engagement={
                        "points": hit.get("points", 0),
                        "comments": hit.get("num_comments", 0),
                    },
                )
            )
        return tutorials[:limit]
