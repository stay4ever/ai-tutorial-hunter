"""Base class for all content sources."""

from __future__ import annotations

from abc import ABC, abstractmethod

import httpx

from ai_tutorial_hunter.models.tutorial import Tutorial
from ai_tutorial_hunter.models.trend import Trend


class BaseSource(ABC):
    """Abstract base for source adapters (YouTube, GitHub, Reddit, etc.)."""

    name: str = "base"
    base_url: str = ""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "AI-Tutorial-Hunter/0.1"},
        )

    async def close(self) -> None:
        await self._client.aclose()

    @abstractmethod
    async def fetch_trending(self, limit: int = 20) -> list[Trend]:
        """Fetch currently trending topics from this source."""
        ...

    @abstractmethod
    async def search_tutorials(self, query: str, limit: int = 20) -> list[Tutorial]:
        """Search for tutorials matching a query."""
        ...

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
