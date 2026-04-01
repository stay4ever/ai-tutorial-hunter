"""Gap Analyzer agent — identifies topics people search for but lack quality tutorials."""

from __future__ import annotations

import logging
from collections import Counter

from ai_tutorial_hunter.models.trend import Trend
from ai_tutorial_hunter.models.tutorial import Tutorial

logger = logging.getLogger(__name__)


class GapResult:
    """A topic where demand exceeds supply of quality tutorials."""

    def __init__(
        self,
        topic: str,
        demand_score: float,
        supply_count: int,
        avg_quality: float,
        gap_score: float,
    ) -> None:
        self.topic = topic
        self.demand_score = demand_score
        self.supply_count = supply_count
        self.avg_quality = avg_quality
        self.gap_score = gap_score

    def __repr__(self) -> str:
        return (
            f"GapResult(topic='{self.topic}', gap={self.gap_score:.1f}, "
            f"demand={self.demand_score:.0f}, supply={self.supply_count}, "
            f"avg_quality={self.avg_quality:.0f})"
        )


class GapAnalyzer:
    """Compares trending topics against available tutorial supply."""

    def analyze(
        self,
        trends: list[Trend],
        tutorials: list[Tutorial],
        min_gap_score: float = 30.0,
    ) -> list[GapResult]:
        """Find topics with high demand but low/poor tutorial supply.

        Gap score = demand_score * (1 - supply_factor) * (1 - quality_factor)
        High gap = people want it, but there aren't enough good tutorials.
        """
        logger.info(
            "Analyzing gaps: %d trends vs %d tutorials", len(trends), len(tutorials),
        )

        # Map tutorials to topics
        topic_tutorials: dict[str, list[Tutorial]] = {}
        for t in tutorials:
            key = t.topic.lower().strip()
            topic_tutorials.setdefault(key, []).append(t)

        gaps: list[GapResult] = []

        for trend in trends:
            topic_key = trend.topic.lower().strip()[:50]
            demand = trend.velocity * max(trend.volume, 1) ** 0.5

            matching = topic_tutorials.get(topic_key, [])
            supply_count = len(matching)

            # Supply factor: 0 (no tutorials) to 1 (many tutorials)
            supply_factor = min(1.0, supply_count / 20)

            # Quality factor: avg quality of what exists
            avg_quality = 0.0
            if matching:
                avg_quality = sum(t.quality_score for t in matching) / len(matching)
            quality_factor = avg_quality / 100

            gap_score = demand * (1 - supply_factor) * (1 - quality_factor * 0.5)

            if gap_score >= min_gap_score:
                gaps.append(
                    GapResult(
                        topic=trend.topic,
                        demand_score=demand,
                        supply_count=supply_count,
                        avg_quality=avg_quality,
                        gap_score=gap_score,
                    )
                )

        gaps.sort(key=lambda g: g.gap_score, reverse=True)
        logger.info("Found %d content gaps above threshold %.0f", len(gaps), min_gap_score)
        return gaps
