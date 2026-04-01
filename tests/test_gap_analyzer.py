"""Tests for the gap analyzer agent."""

from ai_tutorial_hunter.agents.gap_analyzer import GapAnalyzer
from ai_tutorial_hunter.models.trend import Trend
from ai_tutorial_hunter.models.tutorial import Tutorial


class TestGapAnalyzer:
    def setup_method(self):
        self.analyzer = GapAnalyzer()

    def test_high_demand_no_supply_creates_gap(self):
        trends = [Trend(topic="quantum ML", query="quantum ML", velocity=80, volume=1000)]
        tutorials: list[Tutorial] = []  # No tutorials available
        gaps = self.analyzer.analyze(trends, tutorials, min_gap_score=0)
        assert len(gaps) > 0
        assert gaps[0].supply_count == 0

    def test_high_supply_reduces_gap(self):
        trends = [Trend(topic="python basics", query="python basics", velocity=10, volume=100)]
        tutorials = [
            Tutorial(title=f"Python Tutorial {i}", url=f"https://ex.com/{i}", source="github", topic="python basics", quality_score=80)
            for i in range(20)
        ]
        gaps = self.analyzer.analyze(trends, tutorials, min_gap_score=0)
        # With 20 tutorials, gap should be low or zero
        if gaps:
            assert gaps[0].gap_score < 50

    def test_empty_inputs(self):
        assert self.analyzer.analyze([], []) == []
