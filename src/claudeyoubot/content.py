"""Steps 2, 4, 5: script, video prompt and thumbnail prompt, each refined N times."""

from __future__ import annotations

from . import prompts
from .llm import LLM
from .refine import RefineResult, refine
from .trends import Topic


def write_script(llm: LLM, topic: Topic, minutes: int = 8, rounds: int = 5) -> RefineResult:
    topic_text = f"{topic.title}\nWhy it's trending: {topic.reason}\nReference: {topic.link}"
    return refine(
        llm,
        prompts.SCRIPT_SYSTEM,
        prompts.SCRIPT_PROMPT.format(minutes=minutes, topic=topic_text),
        prompts.SCRIPT_CRITERIA,
        rounds,
    )


def write_video_prompt(llm: LLM, script: str, rounds: int = 5) -> RefineResult:
    return refine(
        llm,
        prompts.VIDEO_SYSTEM,
        prompts.VIDEO_PROMPT.format(script=script),
        prompts.VIDEO_CRITERIA,
        rounds,
    )


def write_thumbnail_prompt(llm: LLM, title: str, script: str, rounds: int = 5) -> RefineResult:
    return refine(
        llm,
        prompts.THUMBNAIL_SYSTEM,
        prompts.THUMBNAIL_PROMPT.format(title=title, summary=script[:2000]),
        prompts.THUMBNAIL_CRITERIA,
        rounds,
    )
