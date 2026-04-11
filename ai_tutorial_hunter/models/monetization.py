"""Monetization model — determines which curated content is free vs paid."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class AccessTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"


class MonetizationRule(BaseModel):
    """Rules for classifying content into free or premium tiers.

    Free content strategy (20% — minimal funnel entry):
    - Beginner-level tutorials that are also older than 30 days → both conditions required
    - Top 3 tutorials per weekly digest → taste of quality
    - Gap analysis results (what's missing) → build community trust

    Premium content strategy (80% — monetize):
    - All intermediate and advanced content → always premium regardless of age
    - Recent beginner content (< 30 days old) → speed advantage
    - Full ranked tutorial lists with deep scores → complete intelligence
    - Real-time trend alerts (< 24h old) → speed advantage
    - Personalized recommendations → tailored experience
    - API access for integration → B2B value
    - Content gap opportunities → for creators/businesses
    - Historical trend data & analytics → strategic insights
    """

    # Thresholds
    free_max_results_per_digest: int = Field(default=3)
    free_delay_hours: int = Field(default=720)  # 30 days — both conditions must apply
    premium_realtime_window_hours: int = Field(default=24)

    # Free difficulties — free only when ALSO older than free_delay_hours
    free_difficulties: list[str] = Field(default=["beginner"])

    # Hard cap: free tutorials cannot exceed this fraction of any batch
    free_ratio_cap: float = Field(default=0.20)

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

    Strategy (80% paid / 20% free):
    - Intermediate or Advanced content → always PREMIUM regardless of age
    - Beginner + recent (< 30 days) → PREMIUM (early-access value)
    - Beginner + old (≥ 30 days) → FREE (minimal funnel entry)

    Note: a hard 20% cap is enforced in classify_tiers() after this function
    runs across the full batch, so the free ratio never exceeds free_ratio_cap.
    """
    if rule is None:
        rule = MonetizationRule()

    # Non-beginner content is always premium — depth and recency drive value
    if difficulty not in rule.free_difficulties:
        return AccessTier.PREMIUM

    # Beginner content is only free when it is also sufficiently old
    if age_hours >= rule.free_delay_hours:
        return AccessTier.FREE

    # Beginner but still recent — premium for the early-access window
    return AccessTier.PREMIUM


# Pricing tiers for reference
PRICING = {
    "free": {
        "price": 0,
        "features": [
            "Weekly digest (top 3 tutorials)",
            "Beginner-level content older than 30 days",
            "Trend overview (titles only)",
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
