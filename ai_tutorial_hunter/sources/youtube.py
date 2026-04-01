"""YouTube source — discovers trending AI tutorial videos."""

from __future__ import annotations

from datetime import datetime, timezone

from ai_tutorial_hunter.config.settings import get_settings
from ai_tutorial_hunter.models.trend import Trend
from ai_tutorial_hunter.models.tutorial import Tutorial
from ai_tutorial_hunter.sources.base import BaseSource


class YouTubeSource(BaseSource):
    name = "youtube"
    base_url = "https://www.googleapis.com/youtube/v3"

    async def fetch_trending(self, limit: int = 20) -> list[Trend]:
        """Find trending AI tutorial videos by search volume."""
        queries = [
            "AI tutorial 2026",
            "LLM tutorial",
            "machine learning beginner",
            "AI agents tutorial",
            "RAG tutorial",
        ]
        trends: list[Trend] = []
        api_key = get_settings().youtube_api_key
        if not api_key:
            return []

        for q in queries:
            resp = await self._client.get(
                f"{self.base_url}/search",
                params={
                    "part": "snippet",
                    "q": q,
                    "type": "video",
                    "order": "viewCount",
                    "publishedAfter": "2026-01-01T00:00:00Z",
                    "maxResults": 5,
                    "key": api_key,
                },
            )
            if resp.status_code != 200:
                continue

            data = resp.json()
            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                trends.append(
                    Trend(
                        topic=snippet.get("title", q)[:100],
                        query=q,
                        velocity=50.0,  # Estimated; real velocity requires stats API
                        volume=0,
                        sources=["youtube"],
                        category="",
                    )
                )
        return trends[:limit]

    async def search_tutorials(self, query: str, limit: int = 20) -> list[Tutorial]:
        """Search YouTube for tutorial videos."""
        api_key = get_settings().youtube_api_key
        if not api_key:
            return []

        resp = await self._client.get(
            f"{self.base_url}/search",
            params={
                "part": "snippet",
                "q": f"{query} tutorial",
                "type": "video",
                "order": "relevance",
                "maxResults": min(limit, 25),
                "key": api_key,
            },
        )
        if resp.status_code != 200:
            return []

        data = resp.json()
        video_ids = [
            item["id"]["videoId"]
            for item in data.get("items", [])
            if item.get("id", {}).get("videoId")
        ]

        # Fetch stats for engagement metrics
        stats_map: dict[str, dict] = {}
        if video_ids:
            stats_resp = await self._client.get(
                f"{self.base_url}/videos",
                params={
                    "part": "statistics",
                    "id": ",".join(video_ids),
                    "key": api_key,
                },
            )
            if stats_resp.status_code == 200:
                for item in stats_resp.json().get("items", []):
                    s = item.get("statistics", {})
                    stats_map[item["id"]] = {
                        "views": int(s.get("viewCount", 0)),
                        "likes": int(s.get("likeCount", 0)),
                        "comments": int(s.get("commentCount", 0)),
                    }

        tutorials: list[Tutorial] = []
        for item in data.get("items", []):
            video_id = item.get("id", {}).get("videoId", "")
            snippet = item.get("snippet", {})
            published = None
            if snippet.get("publishedAt"):
                published = datetime.fromisoformat(
                    snippet["publishedAt"].replace("Z", "+00:00")
                )

            tutorials.append(
                Tutorial(
                    title=snippet.get("title", ""),
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    source="youtube",
                    author=snippet.get("channelTitle", ""),
                    published_at=published,
                    topic=query,
                    tags=[],
                    content_type="video",
                    summary=snippet.get("description", "")[:500],
                    engagement=stats_map.get(video_id, {}),
                )
            )
        return tutorials[:limit]
