"""Content Crawler agent — discovers tutorials matching trending topics."""

from __future__ import annotations

import asyncio
import logging

from ai_tutorial_hunter.models.trend import Trend
from ai_tutorial_hunter.models.tutorial import Tutorial
from ai_tutorial_hunter.sources.base import BaseSource
from ai_tutorial_hunter.sources.github import GitHubSource
from ai_tutorial_hunter.sources.reddit import RedditSource
from ai_tutorial_hunter.sources.hackernews import HackerNewsSource
from ai_tutorial_hunter.sources.youtube import YouTubeSource
from ai_tutorial_hunter.sources.arxiv import ArXivSource
from ai_tutorial_hunter.sources.medium import MediumSource

logger = logging.getLogger(__name__)


class ContentCrawler:
    """Searches all sources for tutorials matching given trends."""

    def __init__(self, sources: list[BaseSource] | None = None) -> None:
        self.sources = sources or [
            GitHubSource(),
            RedditSource(),
            HackerNewsSource(),
            YouTubeSource(),
            ArXivSource(),
            MediumSource(),
        ]

    async def crawl(
        self, trends: list[Trend], max_per_trend: int = 10
    ) -> list[Tutorial]:
        """For each trend, search all sources for matching tutorials."""
        logger.info("Crawling tutorials for %d trends", len(trends))

        all_tutorials: list[Tutorial] = []

        for trend in trends:
            query = trend.query or trend.topic
            logger.info("Searching for: %s", query[:60])

            tasks = [
                source.search_tutorials(query, limit=max_per_trend)
                for source in self.sources
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.warning(
                        "Source %s failed for '%s': %s",
                        self.sources[i].name, query[:30], result,
                    )
                    continue
                for tutorial in result:
                    tutorial.topic = trend.topic
                    tutorial.trending_score = trend.velocity
                all_tutorials.extend(result if not isinstance(result, Exception) else [])

        # Deduplicate by URL
        deduped = self._deduplicate_by_url(all_tutorials)
        logger.info("Discovered %d unique tutorials", len(deduped))
        return deduped

    def _deduplicate_by_url(self, tutorials: list[Tutorial]) -> list[Tutorial]:
        seen_urls: set[str] = set()
        unique: list[Tutorial] = []
        for t in tutorials:
            normalized = t.url.rstrip("/").lower()
            if normalized not in seen_urls:
                seen_urls.add(normalized)
                unique.append(t)
        return unique

    async def close(self) -> None:
        for source in self.sources:
            await source.close()
