"""Step 1: find trending topics."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass

from . import prompts
from .llm import LLM


@dataclass
class Topic:
    title: str
    platform: str = ""
    reason: str = ""
    link: str = ""


def fetch_youtube_trending(api_key: str, region: str = "US", limit: int = 10) -> list[str]:
    """Titles of the current most-popular YouTube videos (YouTube Data API v3)."""
    query = urllib.parse.urlencode(
        {"part": "snippet", "chart": "mostPopular", "regionCode": region,
         "maxResults": limit, "key": api_key}
    )
    url = f"https://www.googleapis.com/youtube/v3/videos?{query}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.load(resp)
    return [
        f"{item['snippet']['title']} (https://youtu.be/{item['id']})"
        for item in data.get("items", [])
    ]


def parse_topics(text: str) -> list[Topic]:
    topics = []
    for line in text.splitlines():
        line = line.strip().lstrip("-*0123456789. ").strip()
        if not line or "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|")] + ["", "", ""]
        topics.append(Topic(*parts[:4]))
    return topics


def find_trending_topics(llm: LLM, count: int = 5, niche: str = "",
                         youtube_titles: list[str] | None = None) -> list[Topic]:
    signals = ""
    if youtube_titles:
        signals = "Live YouTube trending videos right now:\n" + "\n".join(
            f"- {t}" for t in youtube_titles
        )
    prompt = prompts.TRENDS_PROMPT.format(
        count=count,
        niche_clause=f" in the '{niche}' niche" if niche else "",
        signals=signals,
    )
    return parse_topics(llm.complete(prompts.TRENDS_SYSTEM, prompt))[:count]
