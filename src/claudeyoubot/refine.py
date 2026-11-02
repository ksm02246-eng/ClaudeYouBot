"""Draft -> critique -> revise loop used by the script, video prompt and thumbnail steps."""

from __future__ import annotations

from dataclasses import dataclass, field

from .llm import LLM


@dataclass
class Revision:
    round: int
    critique: str
    text: str


@dataclass
class RefineResult:
    final: str
    history: list[Revision] = field(default_factory=list)


def refine(
    llm: LLM, system: str, draft_prompt: str, criteria: str, rounds: int = 5
) -> RefineResult:
    """Write a first draft, then critique and rewrite it `rounds` times."""
    text = llm.complete(system, draft_prompt)
    result = RefineResult(final=text, history=[Revision(0, "", text)])
    for i in range(1, rounds + 1):
        critique = llm.complete(
            system,
            f"Critique this draft against these criteria. List concrete fixes only.\n\n"
            f"Criteria:\n{criteria}\n\nDraft:\n{text}",
        )
        text = llm.complete(
            system,
            f"Rewrite the draft, applying every fix. Return only the new version.\n\n"
            f"Fixes:\n{critique}\n\nDraft:\n{text}",
        )
        result.history.append(Revision(i, critique, text))
    result.final = text
    return result
