"""Reddit source — monitors AI subreddits for trending tutorial content."""

from __future__ import annotations

from datetime import datetime, timezone

from ai_tutorial_hunter.models.trend import Trend
from ai_tutorial_hunter.models.tutorial import Tutorial
from ai_tutorial_hunter.sources.base import BaseSource

AI_SUBREDDITS = [
    "MachineLearning",
    "artificial",
    "learnmachinelearning",
    "deeplearning",
    "LocalLLaMA",
    "ChatGPT",
    "ClaudeAI",
    "StableDiffusion",
    "singularity",
    "LanguageTechnology",
]


class RedditSource(BaseSource):
    name = "reddit"
    base_url = "https://www.reddit.com"

    async def fetch_trending(self, limit: int = 20) -> list[Trend]:
        """Get hot posts from AI subreddits to detect trending topics."""
        trends: list[Trend] = []
        for sub in AI_SUBREDDITS[:5]:
            resp = await self._client.get(
                f"{self.base_url}/r/{sub}/hot.json",
                params={"limit": 10},
                headers={"User-Agent": "AI-Tutorial-Hunter/0.1"},
            )
            if resp.status_code != 200:
                continue

            data = resp.json()
            for post in data.get("data", {}).get("children", []):
                d = post.get("data", {})
                score = d.get("score", 0)
                if score < 50:
                    continue
                trends.append(
                    Trend(
                        topic=d.get("title", "")[:100],
                        query=d.get("title", "")[:100],
                        velocity=score / max(1, d.get("num_comments", 1)),
                        volume=score,
                        sources=["reddit"],
                        category="",
                        related_topics=[sub],
                    )
                )
        trends.sort(key=lambda t: t.volume, reverse=True)
        return trends[:limit]

    async def search_tutorials(self, query: str, limit: int = 20) -> list[Tutorial]:
        """Search Reddit for tutorial posts and linked resources."""
        resp = await self._client.get(
            f"{self.base_url}/search.json",
            params={
                "q": f"{query} (tutorial OR guide OR course OR learn)",
                "sort": "relevance",
                "t": "month",
                "limit": min(limit, 25),
            },
            headers={"User-Agent": "AI-Tutorial-Hunter/0.1"},
        )
        if resp.status_code != 200:
            return []

        data = resp.json()
        tutorials: list[Tutorial] = []
        for post in data.get("data", {}).get("children", []):
            d = post.get("data", {})
            created = datetime.fromtimestamp(d.get("created_utc", 0), tz=timezone.utc)
            url = d.get("url", "")

            # Prefer linked URLs over reddit self-posts
            if url.startswith("https://www.reddit.com"):
                url = f"https://www.reddit.com{d.get('permalink', '')}"

            tutorials.append(
                Tutorial(
                    title=d.get("title", ""),
                    url=url,
                    source="reddit",
                    author=d.get("author", ""),
                    published_at=created,
                    topic=query,
                    tags=[d.get("subreddit", "")],
                    content_type="article",
                    summary=d.get("selftext", "")[:500],
                    engagement={
                        "upvotes": d.get("score", 0),
                        "comments": d.get("num_comments", 0),
                    },
                )
            )
        return tutorials[:limit]
