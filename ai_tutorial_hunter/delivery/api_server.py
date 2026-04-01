"""FastAPI server for browsing curated tutorials and trends."""

from __future__ import annotations

from fastapi import FastAPI, Query

from ai_tutorial_hunter.models.monetization import PRICING, AccessTier
from ai_tutorial_hunter.storage.database import Database


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Tutorial Hunter",
        description="Discover trending AI tutorials, ranked by quality",
        version="0.1.0",
    )
    db = Database()
    db.create_tables()

    @app.get("/api/tutorials")
    def list_tutorials(
        topic: str | None = None,
        difficulty: str | None = None,
        limit: int = Query(default=20, le=100),
    ):
        tutorials = db.get_top_tutorials(limit=limit)
        if topic:
            tutorials = [t for t in tutorials if topic.lower() in t.topic.lower()]
        if difficulty:
            tutorials = [t for t in tutorials if t.difficulty == difficulty]
        return {
            "count": len(tutorials),
            "tutorials": [t.model_dump() for t in tutorials],
        }

    @app.get("/api/tutorials/free")
    def list_free_tutorials(limit: int = Query(default=10, le=50)):
        tutorials = db.get_top_tutorials(limit=100)
        free = [
            t for t in tutorials
            if t.difficulty == "beginner" or t.age_hours > 168
        ]
        return {
            "count": len(free[:limit]),
            "tutorials": [t.model_dump() for t in free[:limit]],
        }

    @app.get("/api/tutorials/premium")
    def list_premium_tutorials(limit: int = Query(default=20, le=100)):
        tutorials = db.get_top_tutorials(limit=100)
        premium = [
            t for t in tutorials
            if t.difficulty != "beginner" and t.age_hours <= 168
        ]
        return {
            "count": len(premium[:limit]),
            "tutorials": [t.model_dump() for t in premium[:limit]],
        }

    @app.get("/api/pricing")
    def get_pricing():
        return PRICING

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
