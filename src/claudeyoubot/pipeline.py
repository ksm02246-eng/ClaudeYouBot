"""Runs the full pipeline: trends -> script -> voice -> video prompt -> thumbnail -> Drive."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings
from .content import write_script, write_thumbnail_prompt, write_video_prompt
from .llm import LLM
from .trends import Topic, fetch_youtube_trending, find_trending_topics
from .voice import TTSProvider, choose_voice, narration_text

Log = Callable[[str], None]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50] or "video"


def run(llm: LLM, tts: TTSProvider, settings: Settings, *, niche: str = "",
        topic_index: int = 0, minutes: int = 8, upload: bool = False,
        log: Log = print) -> Path:
    rounds = settings.refine_rounds

    log("1/6 Finding trending topics")
    yt = None
    if settings.youtube_api_key:
        yt = fetch_youtube_trending(settings.youtube_api_key, settings.youtube_region)
    topics = find_trending_topics(llm, count=5, niche=niche, youtube_titles=yt)
    if not topics:
        raise RuntimeError("No trending topics were returned.")
    topic: Topic = topics[min(topic_index, len(topics) - 1)]
    log(f"    picked: {topic.title}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = Path(settings.output_dir) / f"{stamp}-{_slug(topic.title)}"
    out.mkdir(parents=True, exist_ok=True)

    log(f"2/6 Writing script ({rounds} refinement rounds)")
    script = write_script(llm, topic, minutes=minutes, rounds=rounds)

    log(f"3/6 Comparing {settings.voice_candidates} voices")
    voice, scores = choose_voice(llm, script.final, tts.list_voices(), settings.voice_candidates)
    audio_path = tts.synthesize(narration_text(script.final), voice.id, out / "narration")
    log(f"    chose: {voice.id}")

    log(f"4/6 Writing video prompt ({rounds} refinement rounds)")
    video = write_video_prompt(llm, script.final, rounds=rounds)

    log(f"5/6 Writing thumbnail prompt ({rounds} refinement rounds)")
    thumb = write_thumbnail_prompt(llm, topic.title, script.final, rounds=rounds)

    (out / "script.md").write_text(script.final, encoding="utf-8")
    (out / "video_prompt.md").write_text(video.final, encoding="utf-8")
    (out / "thumbnail_prompt.md").write_text(thumb.final, encoding="utf-8")
    (out / "run.json").write_text(json.dumps({
        "topic": asdict(topic),
        "all_topics": [asdict(t) for t in topics],
        "voice": {"chosen": voice.id, "scores": scores, "audio": audio_path.name},
        "refinements": {
            "script": [asdict(r) for r in script.history],
            "video_prompt": [asdict(r) for r in video.history],
            "thumbnail_prompt": [asdict(r) for r in thumb.history],
        },
    }, indent=2), encoding="utf-8")

    if upload:
        log("6/6 Uploading to Google Drive")
        from .drive import upload_folder

        links = upload_folder(out, settings.google_drive_folder_id,
                              settings.google_credentials_file, settings.google_token_file)
        for link in links:
            log(f"    {link}")
    else:
        log("6/6 Skipping Google Drive upload (pass --upload to enable)")

    log(f"Done: {out}")
    return out
