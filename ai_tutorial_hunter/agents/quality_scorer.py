"""Quality Scorer agent — evaluates and ranks discovered tutorials."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from ai_tutorial_hunter.config.settings import get_settings
from ai_tutorial_hunter.models.score import QualityScore
from ai_tutorial_hunter.models.tutorial import Tutorial
from ai_tutorial_hunter.models.monetization import classify_access, AccessTier

logger = logging.getLogger(__name__)


class QualityScorer:
    """Scores tutorials on relevance, freshness, engagement, depth, and credibility."""

    def score_all(self, tutorials: list[Tutorial]) -> list[Tutorial]:
        """Score and rank a list of tutorials. Returns sorted by final_rank."""
        logger.info("Scoring %d tutorials", len(tutorials))

        for tutorial in tutorials:
            score = self._compute_score(tutorial)
            trend_mult = min(2.0, 1.0 + tutorial.trending_score / 100)
            tutorial.quality_score = score.composite
            tutorial.final_rank = score.final_score(trend_mult)

        tutorials.sort(key=lambda t: t.final_rank, reverse=True)

        # Filter below threshold
        threshold = get_settings().quality_threshold
        above = [t for t in tutorials if t.final_rank >= threshold]
        logger.info(
            "%d tutorials above threshold (%.0f), %d filtered out",
            len(above), threshold, len(tutorials) - len(above),
        )
        return above

    def _compute_score(self, tutorial: Tutorial) -> QualityScore:
        return QualityScore(
            relevance=self._score_relevance(tutorial),
            freshness=self._score_freshness(tutorial),
            engagement=self._score_engagement(tutorial),
            depth=self._score_depth(tutorial),
            credibility=self._score_credibility(tutorial),
        )

    def _score_relevance(self, tutorial: Tutorial) -> float:
        """How relevant is the tutorial to AI/ML topics?"""
        score = 50.0  # Base — we already filtered by query
        title_lower = tutorial.title.lower()
        high_value = ["tutorial", "guide", "how to", "step by step", "from scratch", "hands-on"]
        for kw in high_value:
            if kw in title_lower:
                score += 10
        if tutorial.topic and tutorial.topic.lower() in title_lower:
            score += 15
        return min(100.0, score)

    def _score_freshness(self, tutorial: Tutorial) -> float:
        """Newer content scores higher."""
        if not tutorial.published_at:
            return 40.0
        age_hours = tutorial.age_hours
        if age_hours < 24:
            return 100.0
        if age_hours < 72:
            return 90.0
        if age_hours < 168:  # 1 week
            return 80.0
        if age_hours < 720:  # 1 month
            return 60.0
        if age_hours < 2160:  # 3 months
            return 40.0
        return 20.0

    def _score_engagement(self, tutorial: Tutorial) -> float:
        """Higher engagement relative to age = better."""
        total = tutorial.total_engagement
        if total == 0:
            return 30.0
        age = max(tutorial.age_hours, 1)
        velocity = total / age  # Engagement per hour

        if velocity > 100:
            return 100.0
        if velocity > 50:
            return 90.0
        if velocity > 10:
            return 75.0
        if velocity > 1:
            return 60.0
        return 40.0

    def _score_depth(self, tutorial: Tutorial) -> float:
        """Estimate depth from content type and summary length."""
        score = 50.0
        if tutorial.content_type == "repository":
            score += 20  # Code repos tend to be hands-on
        if tutorial.content_type == "course":
            score += 25
        if tutorial.content_type == "paper":
            score += 15
        if tutorial.content_type == "video":
            score += 10
        if len(tutorial.summary) > 200:
            score += 10
        if tutorial.tags:
            score += min(10, len(tutorial.tags) * 2)
        return min(100.0, score)

    def _score_credibility(self, tutorial: Tutorial) -> float:
        """Base credibility on source and author signals."""
        source_scores = {
            "arxiv": 85.0,
            "github": 70.0,
            "youtube": 60.0,
            "medium": 55.0,
            "hackernews": 65.0,
            "reddit": 50.0,
        }
        score = source_scores.get(tutorial.source, 50.0)
        if tutorial.author:
            score += 5
        return min(100.0, score)

    def classify_tiers(self, tutorials: list[Tutorial]) -> dict[str, AccessTier]:
        """Classify each tutorial as free or premium."""
        tiers: dict[str, AccessTier] = {}
        for t in tutorials:
            tiers[t.id] = classify_access(
                difficulty=t.difficulty,
                age_hours=t.age_hours,
                quality_score=t.quality_score,
                is_trending=t.trending_score > 30,
            )
        return tiers
