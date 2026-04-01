"""SQLAlchemy-based storage for tutorials, trends, and pipeline runs."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ai_tutorial_hunter.config.settings import get_settings
from ai_tutorial_hunter.models.tutorial import Tutorial
from ai_tutorial_hunter.models.trend import Trend


class Base(DeclarativeBase):
    pass


class TutorialRow(Base):
    __tablename__ = "tutorials"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    source = Column(String, nullable=False)
    author = Column(String, default="")
    published_at = Column(DateTime, nullable=True)
    discovered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    topic = Column(String, default="")
    tags_json = Column(Text, default="[]")
    difficulty = Column(String, default="intermediate")
    content_type = Column(String, default="article")
    summary = Column(Text, default="")
    engagement_json = Column(Text, default="{}")
    quality_score = Column(Float, default=0.0)
    trending_score = Column(Float, default=0.0)
    final_rank = Column(Float, default=0.0)


class TrendRow(Base):
    __tablename__ = "trends"

    id = Column(String, primary_key=True)
    topic = Column(String, nullable=False)
    query = Column(String, nullable=False)
    velocity = Column(Float, default=0.0)
    volume = Column(Integer, default=0)
    sources_json = Column(Text, default="[]")
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    category = Column(String, default="")


class Database:
    """Simple database layer for persisting pipeline results."""

    def __init__(self, url: str | None = None) -> None:
        self._url = url or get_settings().database_url
        self._engine = create_engine(self._url, echo=False)
        self._session_factory = sessionmaker(bind=self._engine)

    def create_tables(self) -> None:
        Base.metadata.create_all(self._engine)

    def save_tutorials(self, tutorials: list[Tutorial]) -> int:
        """Upsert tutorials. Returns count of new inserts."""
        count = 0
        with self._session_factory() as session:
            for t in tutorials:
                existing = session.query(TutorialRow).filter_by(url=t.url).first()
                if existing:
                    existing.quality_score = t.quality_score
                    existing.final_rank = t.final_rank
                    existing.trending_score = t.trending_score
                    if t.summary:
                        existing.summary = t.summary
                else:
                    row = TutorialRow(
                        id=t.id,
                        title=t.title,
                        url=t.url,
                        source=t.source,
                        author=t.author,
                        published_at=t.published_at,
                        discovered_at=t.discovered_at,
                        topic=t.topic,
                        tags_json=json.dumps(t.tags),
                        difficulty=t.difficulty,
                        content_type=t.content_type,
                        summary=t.summary,
                        engagement_json=json.dumps(t.engagement),
                        quality_score=t.quality_score,
                        trending_score=t.trending_score,
                        final_rank=t.final_rank,
                    )
                    session.add(row)
                    count += 1
            session.commit()
        return count

    def save_trends(self, trends: list[Trend]) -> int:
        count = 0
        with self._session_factory() as session:
            for t in trends:
                existing = session.query(TrendRow).filter_by(
                    topic=t.topic[:50]
                ).first()
                if existing:
                    existing.velocity = t.velocity
                    existing.volume = t.volume
                else:
                    row = TrendRow(
                        id=t.id,
                        topic=t.topic,
                        query=t.query,
                        velocity=t.velocity,
                        volume=t.volume,
                        sources_json=json.dumps(t.sources),
                        first_seen=t.first_seen,
                        category=t.category,
                    )
                    session.add(row)
                    count += 1
            session.commit()
        return count

    def get_top_tutorials(self, limit: int = 20) -> list[Tutorial]:
        with self._session_factory() as session:
            rows = (
                session.query(TutorialRow)
                .order_by(TutorialRow.final_rank.desc())
                .limit(limit)
                .all()
            )
            return [
                Tutorial(
                    id=r.id,
                    title=r.title,
                    url=r.url,
                    source=r.source,
                    author=r.author,
                    published_at=r.published_at,
                    discovered_at=r.discovered_at,
                    topic=r.topic,
                    tags=json.loads(r.tags_json),
                    difficulty=r.difficulty,
                    content_type=r.content_type,
                    summary=r.summary,
                    engagement=json.loads(r.engagement_json),
                    quality_score=r.quality_score,
                    trending_score=r.trending_score,
                    final_rank=r.final_rank,
                )
                for r in rows
            ]
