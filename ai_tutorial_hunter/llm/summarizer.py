"""LLM-powered summarizer for tutorial content."""

from __future__ import annotations

import logging

from ai_tutorial_hunter.config.settings import get_settings
from ai_tutorial_hunter.llm.claude_cli_client import ClaudeCLIClient
from ai_tutorial_hunter.models.tutorial import Tutorial

logger = logging.getLogger(__name__)


class Summarizer:
    """Uses Claude to generate concise tutorial summaries."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = ClaudeCLIClient()
        self._model = settings.llm_model

    def summarize(self, tutorial: Tutorial) -> str:
        """Generate a concise summary of a tutorial."""
        if not tutorial.summary and not tutorial.title:
            return ""

        content = f"Title: {tutorial.title}\n"
        if tutorial.author:
            content += f"Author: {tutorial.author}\n"
        if tutorial.summary:
            content += f"Description: {tutorial.summary}\n"
        content += f"Source: {tutorial.source}\n"
        content += f"Type: {tutorial.content_type}\n"

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=200,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Summarize this AI tutorial in 2-3 sentences. "
                            "Focus on what the reader will learn and the key topics covered. "
                            "Be specific and practical.\n\n"
                            f"{content}"
                        ),
                    }
                ],
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.warning("Summarization failed for '%s': %s", tutorial.title[:50], e)
            return tutorial.summary

    def batch_summarize(self, tutorials: list[Tutorial]) -> list[Tutorial]:
        """Summarize multiple tutorials, updating them in place."""
        for tutorial in tutorials:
            if not tutorial.summary or len(tutorial.summary) < 50:
                tutorial.summary = self.summarize(tutorial)
        return tutorials
