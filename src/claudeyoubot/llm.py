"""Thin LLM interface so the pipeline can run against Claude or a test fake."""

from __future__ import annotations

from typing import Protocol


class LLM(Protocol):
    def complete(self, system: str, prompt: str) -> str: ...


class ClaudeLLM:
    """Calls Claude through the official Anthropic SDK."""

    def __init__(self, model: str = "claude-opus-5-5", effort: str = "high"):
        import anthropic

        self._client = anthropic.Anthropic()
        self.model = model
        self.effort = effort

    def complete(self, system: str, prompt: str) -> str:
        response = self._client.beta.messages.create(
            model=self.model,
            max_tokens=16000,
            system=system,
            thinking={"type": "adaptive"},
            output_config={"effort": self.effort},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            messages=[{"role": "user", "content": prompt}],
        )
        if response.stop_reason == "refusal":
            raise RuntimeError("Claude declined this request; try rephrasing the topic.")
        return "".join(b.text for b in response.content if b.type == "text").strip()
