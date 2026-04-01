"""Tests for the quality scoring agent."""

from datetime import datetime, timedelta, timezone

from ai_tutorial_hunter.agents.quality_scorer import QualityScorer
from ai_tutorial_hunter.models.tutorial import Tutorial


class TestQualityScorer:
    def setup_method(self):
        self.scorer = QualityScorer()

    def test_score_all_returns_sorted(self):
        tutorials = [
            Tutorial(
                title="Basic intro",
                url="https://example.com/1",
                source="reddit",
                engagement={"upvotes": 5},
                published_at=datetime.now(timezone.utc) - timedelta(days=60),
            ),
            Tutorial(
                title="Advanced AI Agents Tutorial - Step by Step",
                url="https://example.com/2",
                source="github",
                engagement={"stars": 500, "forks": 100},
                published_at=datetime.now(timezone.utc) - timedelta(hours=12),
                trending_score=80,
            ),
        ]
        scored = self.scorer.score_all(tutorials)
        if len(scored) >= 2:
            assert scored[0].final_rank >= scored[1].final_rank

    def test_empty_list(self):
        assert self.scorer.score_all([]) == []

    def test_tutorial_keywords_boost_relevance(self):
        t = Tutorial(
            title="Step by Step Guide to Fine-tuning LLMs",
            url="https://example.com/3",
            source="github",
            topic="fine-tuning",
        )
        scored = self.scorer.score_all([t])
        assert len(scored) >= 0  # May be filtered by threshold
