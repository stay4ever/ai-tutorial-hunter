"""LLM-powered classifier for topic and difficulty detection."""

from __future__ import annotations

import json
import logging

from ai_tutorial_hunter.config.settings import get_settings
from ai_tutorial_hunter.config.topics import TOPIC_TAXONOMY, DIFFICULTY_LEVELS
from ai_tutorial_hunter.llm.claude_cli_client import ClaudeCLIClient
from ai_tutorial_hunter.models.tutorial import Tutorial

logger = logging.getLogger(__name__)


class Classifier:
    """Uses Claude to classify tutorials by topic and difficulty."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = ClaudeCLIClient()
        self._model = settings.llm_model
        self._categories = list(TOPIC_TAXONOMY.keys())

    def classify(self, tutorial: Tutorial) -> Tutorial:
        """Classify a tutorial's topic and difficulty level."""
        content = f"Title: {tutorial.title}\n"
        if tutorial.summary:
            content += f"Summary: {tutorial.summary[:300]}\n"
        if tutorial.tags:
            content += f"Tags: {', '.join(tutorial.tags[:10])}\n"
        content += f"Content type: {tutorial.content_type}\n"

        categories_str = ", ".join(self._categories)
        difficulties_str = ", ".join(DIFFICULTY_LEVELS)

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Classify this AI tutorial. Respond with ONLY valid JSON.\n\n"
                            f"Categories: {categories_str}\n"
                            f"Difficulty levels: {difficulties_str}\n\n"
                            f"Tutorial:\n{content}\n\n"
                            'Respond: {"category": "...", "difficulty": "...", "tags": ["...", "..."]}'
                        ),
                    }
                ],
            )
            text = response.content[0].text.strip()
            # Extract JSON from response
            if "{" in text:
                text = text[text.index("{"):text.rindex("}") + 1]
            result = json.loads(text)

            if result.get("category") in self._categories:
                tutorial.topic = result["category"]
            if result.get("difficulty") in DIFFICULTY_LEVELS:
                tutorial.difficulty = result["difficulty"]
            if result.get("tags"):
                tutorial.tags = list(set(tutorial.tags + result["tags"][:5]))

        except Exception as e:
            logger.warning("Classification failed for '%s': %s", tutorial.title[:50], e)

        return tutorial

    def batch_classify(self, tutorials: list[Tutorial]) -> list[Tutorial]:
        """Classify multiple tutorials."""
        for tutorial in tutorials:
            self.classify(tutorial)
        return tutorials
