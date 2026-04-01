"""Trend data model."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class Trend(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    topic: str
    query: str  # The search query driving this trend
    velocity: float = 0.0  # Rate of search volume increase
    volume: int = 0  # Current search volume estimate
    sources: list[str] = Field(default_factory=list)  # Where detected
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    peak_predicted: datetime | None = None
    category: str = ""
    related_topics: list[str] = Field(default_factory=list)

    @property
    def is_accelerating(self) -> bool:
        return self.velocity > 0

    @property
    def trend_multiplier(self) -> float:
        """Boost factor for content scoring (1.0–2.0)."""
        if self.velocity <= 0:
            return 1.0
        return min(2.0, 1.0 + self.velocity / 100)
