"""ArXiv source — discovers AI research papers with tutorial/educational value."""

from __future__ import annotations

from datetime import datetime, timezone

import feedparser

from ai_tutorial_hunter.models.trend import Trend
from ai_tutorial_hunter.models.tutorial import Tutorial
from ai_tutorial_hunter.sources.base import BaseSource


class ArXivSource(BaseSource):
    name = "arxiv"
    base_url = "http://export.arxiv.org/api/query"

    async def fetch_trending(self, limit: int = 20) -> list[Trend]:
        """Fetch recent popular AI papers from ArXiv."""
        resp = await self._client.get(
            self.base_url,
            params={
                "search_query": "cat:cs.AI OR cat:cs.LG OR cat:cs.CL",
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "max_results": min(limit, 30),
            },
        )
        if resp.status_code != 200:
            return []

        feed = feedparser.parse(resp.text)
        trends: list[Trend] = []
        for entry in feed.entries:
            trends.append(
                Trend(
                    topic=entry.get("title", "").replace("\n", " ")[:100],
                    query=entry.get("title", "")[:100],
                    velocity=10.0,
                    volume=0,
                    sources=["arxiv"],
                    category="research",
                    related_topics=[
                        tag.get("term", "")
                        for tag in entry.get("tags", [])[:5]
                    ],
                )
            )
        return trends[:limit]

    async def search_tutorials(self, query: str, limit: int = 20) -> list[Tutorial]:
        """Search ArXiv for papers with tutorial/survey content."""
        resp = await self._client.get(
            self.base_url,
            params={
                "search_query": f"all:{query} AND (all:tutorial OR all:survey OR all:guide)",
                "sortBy": "relevance",
                "max_results": min(limit, 30),
            },
        )
        if resp.status_code != 200:
            return []

        feed = feedparser.parse(resp.text)
        tutorials: list[Tutorial] = []
        for entry in feed.entries:
            published = None
            if entry.get("published"):
                try:
                    published = datetime.fromisoformat(
                        entry["published"].replace("Z", "+00:00")
                    )
                except ValueError:
                    pass

            authors = ", ".join(
                a.get("name", "") for a in entry.get("authors", [])[:3]
            )

            tutorials.append(
                Tutorial(
                    title=entry.get("title", "").replace("\n", " "),
                    url=entry.get("link", ""),
                    source="arxiv",
                    author=authors,
                    published_at=published,
                    topic=query,
                    tags=[t.get("term", "") for t in entry.get("tags", [])[:10]],
                    content_type="paper",
                    summary=entry.get("summary", "").replace("\n", " ")[:500],
                    engagement={},
                )
            )
        return tutorials[:limit]
