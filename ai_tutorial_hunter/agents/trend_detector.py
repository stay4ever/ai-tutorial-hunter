"""Trend Detector agent — monitors sources and identifies rising AI topics."""

from __future__ import annotations

import asyncio
import logging

from ai_tutorial_hunter.models.trend import Trend
from ai_tutorial_hunter.sources.base import BaseSource
from ai_tutorial_hunter.sources.github import GitHubSource
from ai_tutorial_hunter.sources.reddit import RedditSource
from ai_tutorial_hunter.sources.hackernews import HackerNewsSource
from ai_tutorial_hunter.sources.youtube import YouTubeSource
from ai_tutorial_hunter.sources.arxiv import ArXivSource
from ai_tutorial_hunter.sources.medium import MediumSource

logger = logging.getLogger(__name__)


class TrendDetector:
    """Aggregates trends from multiple sources and ranks by velocity."""

    def __init__(self, sources: list[BaseSource] | None = None) -> None:
        self.sources = sources or [
            GitHubSource(),
            RedditSource(),
            HackerNewsSource(),
            YouTubeSource(),
            ArXivSource(),
            MediumSource(),
        ]

    async def detect(self, limit: int = 30) -> list[Trend]:
        """Run trend detection across all sources concurrently."""
        logger.info("Starting trend detection across %d sources", len(self.sources))

        tasks = [source.fetch_trending(limit=20) for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_trends: list[Trend] = []
        for i, result in enumerate(results):
            source_name = self.sources[i].name
            if isinstance(result, Exception):
                logger.warning("Source %s failed: %s", source_name, result)
                continue
            logger.info("Source %s returned %d trends", source_name, len(result))
            all_trends.extend(result)

        # Deduplicate by similar topics
        deduped = self._deduplicate(all_trends)

        # Rank by velocity * volume
        deduped.sort(key=lambda t: t.velocity * max(t.volume, 1), reverse=True)

        logger.info("Detected %d unique trends", len(deduped))
        return deduped[:limit]

    def _deduplicate(self, trends: list[Trend]) -> list[Trend]:
        """Simple deduplication by normalized topic name."""
        seen: dict[str, Trend] = {}
        for trend in trends:
            key = trend.topic.lower().strip()[:50]
            if key in seen:
                # Merge: keep higher velocity, combine sources
                existing = seen[key]
                if trend.velocity > existing.velocity:
                    trend.sources = list(set(existing.sources + trend.sources))
                    trend.volume = max(trend.volume, existing.volume)
                    seen[key] = trend
                else:
                    existing.sources = list(set(existing.sources + trend.sources))
                    existing.volume = max(existing.volume, trend.volume)
            else:
                seen[key] = trend
        return list(seen.values())

    async def close(self) -> None:
        for source in self.sources:
            await source.close()
