"""Step 3: compare candidate voices and synthesise narration with the best one."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from . import prompts
from .llm import LLM


@dataclass
class Voice:
    id: str
    description: str


class TTSProvider(Protocol):
    def list_voices(self) -> list[Voice]: ...
    def synthesize(self, text: str, voice_id: str, out_path: Path) -> Path: ...


class SilentTTS:
    """Offline stand-in used for dry runs and tests: writes the text instead of audio."""

    VOICES = (
        Voice("calm-narrator", "warm, calm male narrator, documentary style"),
        Voice("energetic-host", "upbeat female host, fast pace"),
        Voice("deep-storyteller", "deep, dramatic storyteller"),
        Voice("friendly-explainer", "clear, friendly teacher voice"),
        Voice("news-anchor", "neutral, authoritative news anchor"),
    )

    def list_voices(self) -> list[Voice]:
        return list(self.VOICES)

    def synthesize(self, text: str, voice_id: str, out_path: Path) -> Path:
        out_path = out_path.with_suffix(".txt")
        out_path.write_text(f"[voice={voice_id}]\n{text}", encoding="utf-8")
        return out_path


class ElevenLabsTTS:
    """ElevenLabs text-to-speech. Needs `pip install .[tts]` and ELEVENLABS_API_KEY."""

    def __init__(self, api_key: str):
        from elevenlabs.client import ElevenLabs

        self._client = ElevenLabs(api_key=api_key)

    def list_voices(self) -> list[Voice]:
        voices = self._client.voices.get_all().voices
        return [
            Voice(v.voice_id, f"{v.name}: {', '.join((v.labels or {}).values())}")
            for v in voices
        ]

    def synthesize(self, text: str, voice_id: str, out_path: Path) -> Path:
        out_path = out_path.with_suffix(".mp3")
        audio = self._client.text_to_speech.convert(
            voice_id=voice_id, text=text, model_id="eleven_multilingual_v2"
        )
        with open(out_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        return out_path


def narration_text(script: str) -> str:
    """Keep NARRATOR lines and drop [visual cues]; fall back to the whole script."""
    lines = [m.group(1).strip() for m in re.finditer(r"NARRATOR:\s*(.+)", script)]
    text = " ".join(lines) if lines else script
    return re.sub(r"\[[^\]]*\]", "", text).strip()


def choose_voice(
    llm: LLM, script: str, voices: list[Voice], candidates: int = 5
) -> tuple[Voice, dict[str, float]]:
    pool = voices[:candidates]
    if not pool:
        raise ValueError("No voices available from the TTS provider.")
    reply = llm.complete(
        prompts.VOICE_SYSTEM,
        prompts.VOICE_PROMPT.format(
            excerpt=narration_text(script)[:1500],
            candidates="\n".join(f"{v.id}: {v.description}" for v in pool),
        ),
    )
    scores: dict[str, float] = {}
    for v in pool:
        m = re.search(rf"{re.escape(v.id)}\s*:\s*(\d+(?:\.\d+)?)", reply)
        scores[v.id] = float(m.group(1)) if m else 0.0
    best = max(pool, key=lambda v: scores[v.id])
    return best, scores
