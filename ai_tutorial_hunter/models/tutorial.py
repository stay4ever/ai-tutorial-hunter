"""Tutorial content model."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class Tutorial(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    title: str
    url: str
    source: str  # youtube, github, medium, arxiv, etc.
    author: str = ""
    published_at: datetime | None = None
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    topic: str = ""
    tags: list[str] = Field(default_factory=list)
    difficulty: str = "intermediate"  # beginner | intermediate | advanced
    content_type: str = "article"  # video | article | repository | course | paper | notebook
    summary: str = ""
    engagement: dict[str, int] = Field(default_factory=dict)
    quality_score: float = 0.0
    trending_score: float = 0.0
    final_rank: float = 0.0

    @property
    def age_hours(self) -> float:
        if not self.published_at:
            return 0.0
        delta = datetime.now(timezone.utc) - self.published_at
        return delta.total_seconds() / 3600

    @property
    def total_engagement(self) -> int:
        return sum(self.engagement.values())
