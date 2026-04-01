"""Tests for data models."""

from datetime import datetime, timedelta, timezone

from ai_tutorial_hunter.models.tutorial import Tutorial
from ai_tutorial_hunter.models.trend import Trend
from ai_tutorial_hunter.models.score import QualityScore
from ai_tutorial_hunter.models.monetization import classify_access, AccessTier


class TestTutorial:
    def test_create_tutorial(self):
        t = Tutorial(title="Learn RAG", url="https://example.com/rag", source="github")
        assert t.title == "Learn RAG"
        assert t.id  # Auto-generated
        assert t.difficulty == "intermediate"

    def test_age_hours(self):
        t = Tutorial(
            title="Test",
            url="https://example.com",
            source="github",
            published_at=datetime.now(timezone.utc) - timedelta(hours=48),
        )
        assert 47 < t.age_hours < 49

    def test_total_engagement(self):
        t = Tutorial(
            title="Test",
            url="https://example.com",
            source="github",
            engagement={"stars": 100, "forks": 20},
        )
        assert t.total_engagement == 120


class TestTrend:
    def test_trend_multiplier_zero_velocity(self):
        t = Trend(topic="test", query="test", velocity=0)
        assert t.trend_multiplier == 1.0

    def test_trend_multiplier_high_velocity(self):
        t = Trend(topic="test", query="test", velocity=200)
        assert t.trend_multiplier == 2.0  # Capped

    def test_is_accelerating(self):
        t = Trend(topic="test", query="test", velocity=10)
        assert t.is_accelerating is True

    def test_not_accelerating(self):
        t = Trend(topic="test", query="test", velocity=-5)
        assert t.is_accelerating is False


class TestQualityScore:
    def test_composite_score(self):
        score = QualityScore(
            relevance=80, freshness=90, engagement=70, depth=85, credibility=60,
        )
        composite = score.composite
        assert 0 < composite <= 100

    def test_grade_a(self):
        score = QualityScore(
            relevance=95, freshness=95, engagement=95, depth=95, credibility=95,
        )
        assert score.grade == "A"

    def test_final_score_with_trend_boost(self):
        score = QualityScore(
            relevance=80, freshness=80, engagement=80, depth=80, credibility=80,
        )
        assert score.final_score(2.0) > score.final_score(1.0)


class TestMonetization:
    def test_beginner_is_free(self):
        tier = classify_access(
            difficulty="beginner", age_hours=1, quality_score=90, is_trending=True,
        )
        assert tier == AccessTier.FREE

    def test_old_content_is_free(self):
        tier = classify_access(
            difficulty="advanced", age_hours=200, quality_score=90, is_trending=True,
        )
        assert tier == AccessTier.FREE

    def test_new_advanced_is_premium(self):
        tier = classify_access(
            difficulty="advanced", age_hours=10, quality_score=90, is_trending=True,
        )
        assert tier == AccessTier.PREMIUM

    def test_new_intermediate_is_premium(self):
        tier = classify_access(
            difficulty="intermediate", age_hours=5, quality_score=80, is_trending=False,
        )
        assert tier == AccessTier.PREMIUM
