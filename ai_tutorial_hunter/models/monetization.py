"""Monetization model — determines which curated content is free vs paid."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class AccessTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"


class MonetizationRule(BaseModel):
    """Rules for classifying content into free or premium tiers.

    Free content strategy (capture & engage):
    - Beginner-level tutorials → low barrier to entry
    - Trending topics digest (titles + summaries only) → hook users
    - Older content (>7 days since discovery) → time-delayed freemium
    - Gap analysis results (what's missing) → build community trust
    - Top 3 tutorials per weekly digest → taste of quality

    Premium content strategy (monetize):
    - Full ranked tutorial lists with deep scores → complete intelligence
    - Real-time trend alerts (< 24h old) → speed advantage
    - Advanced/intermediate curated paths → high-value learning
    - Personalized recommendations → tailored experience
    - API access for integration → B2B value
    - Content gap opportunities → for creators/businesses
    - Historical trend data & analytics → strategic insights
    """

    # Thresholds
    free_max_results_per_digest: int = Field(default=3)
    free_delay_hours: int = Field(default=168)  # 7 days
    premium_realtime_window_hours: int = Field(default=24)

    # Free difficulties
    free_difficulties: list[str] = Field(default=["beginner"])

    # Free content types (summaries only, no deep scores)
    free_includes_scores: bool = Field(default=False)
    free_includes_full_summary: bool = Field(default=False)

    # Premium features
    premium_includes_scores: bool = Field(default=True)
    premium_includes_recommendations: bool = Field(default=True)
    premium_includes_api: bool = Field(default=True)
    premium_includes_gap_opportunities: bool = Field(default=True)
    premium_includes_analytics: bool = Field(default=True)


class ContentAccess(BaseModel):
    """Resolved access tier for a specific tutorial."""
    tutorial_id: str
    tier: AccessTier
    reason: str  # Why this tier was assigned
    preview_available: bool = True  # Free users can always see title + short summary
    full_access: bool = False  # Full scores, deep summary, related content


def classify_access(
    difficulty: str,
    age_hours: float,
    quality_score: float,
    is_trending: bool,
    rule: MonetizationRule | None = None,
) -> AccessTier:
    """Determine whether a tutorial should be free or premium.

    Strategy:
    - Beginner content → FREE (hook new users)
    - Old content (>7 days) → FREE (time-delayed freemium)
    - Hot trending + recent + high quality → PREMIUM (speed advantage)
    - Intermediate/Advanced + high quality → PREMIUM (depth value)
    """
    if rule is None:
        rule = MonetizationRule()

    # Beginner content is always free — build the top of the funnel
    if difficulty in rule.free_difficulties:
        return AccessTier.FREE

    # Old content becomes free — time-delayed freemium
    if age_hours > rule.free_delay_hours:
        return AccessTier.FREE

    # Everything else is premium — real-time, high-quality, advanced
    return AccessTier.PREMIUM


# Pricing tiers for reference
PRICING = {
    "free": {
        "price": 0,
        "features": [
            "Weekly digest (top 3 tutorials)",
            "Beginner-level content",
            "Trend overview (titles only)",
            "7-day delayed access to all content",
        ],
    },
    "pro": {
        "price": 9.99,
        "interval": "month",
        "features": [
            "Daily digest (full ranked lists)",
            "All difficulty levels",
            "Real-time trend alerts",
            "Quality scores and deep summaries",
            "Personalized recommendations",
            "Search and filter all tutorials",
        ],
    },
    "team": {
        "price": 29.99,
        "interval": "month",
        "features": [
            "Everything in Pro",
            "API access (1000 req/day)",
            "Content gap analysis",
            "Historical trend analytics",
            "Slack/Discord integration",
            "Priority support",
        ],
    },
}
