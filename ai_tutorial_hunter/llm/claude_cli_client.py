"""LLM client backed by the local `claude` CLI.

Routes generation through the Claude Code session authenticated on this
machine (a Claude.ai subscription) instead of the Anthropic API, so usage
draws from the subscription's plan limits rather than pay-per-token API
credits.
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ClaudeCLIError(RuntimeError):
    """Raised when the `claude` CLI is unavailable or returns an error."""


@dataclass
class _ContentBlock:
    text: str


@dataclass
class _Message:
    content: list[_ContentBlock] = field(default_factory=list)


class _Messages:
    def __init__(self, binary: str, timeout: int) -> None:
        self._binary = binary
        self._timeout = timeout

    def create(self, *, model: str, messages: list[dict], max_tokens: int | None = None) -> _Message:
        prompt = "\n\n".join(m["content"] for m in messages if m.get("role") == "user")
        cmd = [self._binary, "-p", prompt, "--output-format", "json", "--model", model]

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=self._timeout)
        except subprocess.TimeoutExpired as e:
            raise ClaudeCLIError(f"claude CLI timed out after {self._timeout}s") from e

        if proc.returncode != 0:
            detail = proc.stderr.strip() or proc.stdout.strip()
            raise ClaudeCLIError(f"claude CLI exited {proc.returncode}: {detail[:1000]}")

        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as e:
            raise ClaudeCLIError(f"claude CLI returned non-JSON output: {proc.stdout[:500]}") from e

        if payload.get("is_error"):
            raise ClaudeCLIError(f"claude CLI reported an error: {payload.get('result')}")

        return _Message(content=[_ContentBlock(text=payload.get("result", ""))])


class ClaudeCLIClient:
    """Stand-in for anthropic.Anthropic's `.messages.create()`, backed by the `claude` CLI."""

    def __init__(self, binary: str = "claude", timeout: int = 600) -> None:
        resolved = shutil.which(binary)
        if not resolved:
            raise ClaudeCLIError(
                f"'{binary}' not found on PATH. Install Claude Code and run `claude login`."
            )
        self.messages = _Messages(resolved, timeout)
