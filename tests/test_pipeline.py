import json

from claudeyoubot.config import Settings
from claudeyoubot.pipeline import run
from claudeyoubot.refine import refine
from claudeyoubot.trends import parse_topics
from claudeyoubot.voice import SilentTTS, choose_voice, narration_text


class FakeLLM:
    """Returns canned answers based on the system/prompt so tests run offline."""

    def __init__(self):
        self.calls = []

    def complete(self, system: str, prompt: str) -> str:
        self.calls.append((system, prompt))
        if "trend analyst" in system:
            return (
                "1. AI gadgets of 2026 | YouTube | launch season | https://youtu.be/x\n"
                "2. Budget travel hacks | Instagram | summer reels | \n"
                "not a topic line\n"
            )
        if "casting director" in system:
            return "calm-narrator: 6 - ok\nfriendly-explainer: 9 - clear\nnews-anchor: 4"
        if prompt.startswith("Critique"):
            return "- tighten the hook"
        if prompt.startswith("Rewrite"):
            return f"v{sum(c[1].startswith('Rewrite') for c in self.calls)}"
        return "NARRATOR: Hello there. [wide shot]\nNARRATOR: Welcome back."


def test_parse_topics_skips_noise():
    topics = parse_topics("1. A | YouTube | why | link\nrandom\n- B | X | because")
    assert [t.title for t in topics] == ["A", "B"]
    assert topics[0].link == "link"
    assert topics[1].link == ""


def test_refine_runs_requested_rounds():
    llm = FakeLLM()
    result = refine(llm, "sys", "draft please", "criteria", rounds=5)
    assert len(result.history) == 6  # draft + 5 revisions
    assert result.final == "v5"
    assert len(llm.calls) == 1 + 5 * 2


def test_choose_voice_picks_highest_score():
    voices = SilentTTS().list_voices()
    best, scores = choose_voice(FakeLLM(), "NARRATOR: hi", voices, candidates=5)
    assert best.id == "friendly-explainer"
    assert len(scores) == 5
    assert scores["energetic-host"] == 0.0


def test_narration_text_strips_cues():
    assert narration_text("NARRATOR: Hi [zoom]\n[cut]\nNARRATOR: Bye") == "Hi  Bye"


def test_full_pipeline_dry_run(tmp_path):
    settings = Settings(output_dir=str(tmp_path), refine_rounds=5)
    out = run(FakeLLM(), SilentTTS(), settings, log=lambda _m: None)
    files = {p.name for p in out.iterdir()}
    assert {"script.md", "video_prompt.md", "thumbnail_prompt.md", "run.json",
            "narration.txt"} <= files
    meta = json.loads((out / "run.json").read_text())
    assert meta["topic"]["title"] == "AI gadgets of 2026"
    assert meta["voice"]["chosen"] == "friendly-explainer"
    for step in ("script", "video_prompt", "thumbnail_prompt"):
        assert len(meta["refinements"][step]) == 6


def test_cli_check_reports_missing(monkeypatch, capsys):
    from claudeyoubot.cli import main

    for var in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ELEVENLABS_API_KEY",
                "GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_DRIVE_FOLDER_ID"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: False)
    assert main(["check", "--upload"]) == 1
    out = capsys.readouterr().out
    for var in ("ANTHROPIC_API_KEY", "ELEVENLABS_API_KEY", "GOOGLE_DRIVE_FOLDER_ID"):
        assert var in out
