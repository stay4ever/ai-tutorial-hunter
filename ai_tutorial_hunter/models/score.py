from __future__ import annotations
"""Quality scoring model."""

from pydantic import BaseModel, Field

from ai_tutorial_hunter.config.settings import get_settings


class QualityScore(BaseModel):
    relevance: float = Field(default=0.0, ge=0.0, le=100.0)
    freshness: float = Field(default=0.0, ge=0.0, le=100.0)
    engagement: float = Field(default=0.0, ge=0.0, le=100.0)
    depth: float = Field(default=0.0, ge=0.0, le=100.0)
    credibility: float = Field(default=0.0, ge=0.0, le=100.0)

    @property
    def composite(self) -> float:
        """Weighted composite score."""
        s = get_settings()
        return (
            s.weight_relevance * self.relevance
            + s.weight_freshness * self.freshness
            + s.weight_engagement * self.engagement
            + s.weight_depth * self.depth
            + s.weight_credibility * self.credibility
        )

    def final_score(self, trend_multiplier: float = 1.0) -> float:
        """Composite score boosted by trend multiplier."""
        return self.composite * min(max(trend_multiplier, 1.0), 2.0)

    @property
    def grade(self) -> str:
        score = self.composite
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"
