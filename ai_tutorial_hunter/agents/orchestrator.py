"""Orchestrator — coordinates the full pipeline: detect → crawl → score → analyze."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from ai_tutorial_hunter.agents.trend_detector import TrendDetector
from ai_tutorial_hunter.agents.content_crawler import ContentCrawler
from ai_tutorial_hunter.agents.quality_scorer import QualityScorer
from ai_tutorial_hunter.agents.gap_analyzer import GapAnalyzer, GapResult
from ai_tutorial_hunter.models.trend import Trend
from ai_tutorial_hunter.models.tutorial import Tutorial
from ai_tutorial_hunter.models.monetization import AccessTier

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Output of a full pipeline run."""
    trends: list[Trend] = field(default_factory=list)
    tutorials: list[Tutorial] = field(default_factory=list)
    gaps: list[GapResult] = field(default_factory=list)
    tiers: dict[str, AccessTier] = field(default_factory=dict)


class Orchestrator:
    """Runs the full agentic pipeline end-to-end."""

    def __init__(self) -> None:
        self.trend_detector = TrendDetector()
        self.content_crawler = ContentCrawler()
        self.quality_scorer = QualityScorer()
        self.gap_analyzer = GapAnalyzer()

    async def run(self, max_trends: int = 10) -> PipelineResult:
        """Execute the full discovery pipeline.

        1. Detect trending topics across all sources
        2. Crawl tutorials matching those trends
        3. Score and rank all discovered tutorials
        4. Classify free vs premium access tiers
        5. Analyze content gaps
        """
        logger.info("=== Pipeline starting ===")

        # Step 1: Detect trends
        logger.info("Step 1/5: Detecting trends...")
        trends = await self.trend_detector.detect(limit=max_trends)
        logger.info("Found %d trends", len(trends))

        if not trends:
            logger.warning("No trends detected. Pipeline ending early.")
            return PipelineResult()

        # Step 2: Crawl tutorials
        logger.info("Step 2/5: Crawling tutorials...")
        tutorials = await self.content_crawler.crawl(trends, max_per_trend=10)
        logger.info("Discovered %d tutorials", len(tutorials))

        # Step 3: Score and rank
        logger.info("Step 3/5: Scoring tutorials...")
        scored = self.quality_scorer.score_all(tutorials)
        logger.info("Scored %d tutorials above threshold", len(scored))

        # Step 4: Classify access tiers
        logger.info("Step 4/5: Classifying access tiers...")
        tiers = self.quality_scorer.classify_tiers(scored)
        free_count = sum(1 for t in tiers.values() if t == AccessTier.FREE)
        logger.info("Tiers: %d free, %d premium", free_count, len(tiers) - free_count)

        # Step 5: Gap analysis
        logger.info("Step 5/5: Analyzing content gaps...")
        gaps = self.gap_analyzer.analyze(trends, scored)
        logger.info("Found %d content gaps", len(gaps))

        logger.info("=== Pipeline complete ===")
        return PipelineResult(
            trends=trends,
            tutorials=scored,
            gaps=gaps,
            tiers=tiers,
        )

    async def close(self) -> None:
        await self.trend_detector.close()
        await self.content_crawler.close()
