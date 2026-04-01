"""Medium source — discovers AI tutorials via RSS feeds of top publications."""

from __future__ import annotations

from datetime import datetime, timezone

import feedparser

from ai_tutorial_hunter.models.trend import Trend
from ai_tutorial_hunter.models.tutorial import Tutorial
from ai_tutorial_hunter.sources.base import BaseSource

# Top AI/ML Medium publications with RSS feeds
MEDIUM_FEEDS = [
    "https://towardsdatascience.com/feed",
    "https://medium.com/feed/towards-artificial-intelligence",
    "https://medium.com/feed/@ai.science",
    "https://medium.com/feed/the-generator",
    "https://medium.com/feed/huggingface",
]


class MediumSource(BaseSource):
    name = "medium"
    base_url = "https://medium.com"

    async def fetch_trending(self, limit: int = 20) -> list[Trend]:
        """Parse RSS feeds from top AI publications for trending topics."""
        trends: list[Trend] = []
        for feed_url in MEDIUM_FEEDS:
            resp = await self._client.get(feed_url)
            if resp.status_code != 200:
                continue

            feed = feedparser.parse(resp.text)
            for entry in feed.entries[:5]:
                trends.append(
                    Trend(
                        topic=entry.get("title", "")[:100],
                        query=entry.get("title", "")[:100],
                        velocity=20.0,
                        volume=0,
                        sources=["medium"],
                        category="",
                    )
                )
        return trends[:limit]

    async def search_tutorials(self, query: str, limit: int = 20) -> list[Tutorial]:
        """Search Medium publications for tutorial articles via RSS."""
        tutorials: list[Tutorial] = []
        query_lower = query.lower()

        for feed_url in MEDIUM_FEEDS:
            resp = await self._client.get(feed_url)
            if resp.status_code != 200:
                continue

            feed = feedparser.parse(resp.text)
            for entry in feed.entries:
                title = entry.get("title", "").lower()
                summary = entry.get("summary", "").lower()
                if query_lower not in title and query_lower not in summary:
                    continue

                published = None
                if entry.get("published_parsed"):
                    try:
                        published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    except (TypeError, ValueError):
                        pass

                tutorials.append(
                    Tutorial(
                        title=entry.get("title", ""),
                        url=entry.get("link", ""),
                        source="medium",
                        author=entry.get("author", ""),
                        published_at=published,
                        topic=query,
                        content_type="article",
                        summary=entry.get("summary", "")[:500],
                        engagement={},
                    )
                )
                if len(tutorials) >= limit:
                    return tutorials

        return tutorials[:limit]
