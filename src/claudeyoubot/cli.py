"""Command line entry point: `claudeyoubot run` and `claudeyoubot check`."""

from __future__ import annotations

import argparse
import sys

from .config import Settings


def _check(settings: Settings, upload: bool, real_voice: bool) -> int:
    missing = settings.missing_for(drive=upload, real_voice=real_voice)
    if missing:
        print("Missing settings: " + ", ".join(missing))
        print("Add them to your environment or a .env file (see .env.example).")
        return 1
    print("All required settings are present.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="claudeyoubot")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "check"):
        p = sub.add_parser(name)
        p.add_argument("--upload", action="store_true", help="upload results to Google Drive")
        p.add_argument("--silent-voice", action="store_true",
                       help="skip real TTS and write narration text instead")
    run_p = sub.choices["run"]
    run_p.add_argument("--niche", default="", help="channel niche, e.g. 'tech reviews'")
    run_p.add_argument("--topic-index", type=int, default=0, help="which trending topic to use")
    run_p.add_argument("--minutes", type=int, default=8, help="target video length")
    args = parser.parse_args(argv)

    settings = Settings.from_env()
    real_voice = not args.silent_voice
    code = _check(settings, args.upload, real_voice)
    if args.command == "check" or code:
        return code

    from .llm import ClaudeLLM
    from .pipeline import run
    from .voice import ElevenLabsTTS, SilentTTS

    tts = ElevenLabsTTS(settings.elevenlabs_api_key) if real_voice else SilentTTS()
    run(ClaudeLLM(settings.anthropic_model), tts, settings, niche=args.niche,
        topic_index=args.topic_index, minutes=args.minutes, upload=args.upload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
