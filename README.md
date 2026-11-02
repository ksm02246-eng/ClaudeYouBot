# ClaudeYouBot

A bot that turns what's trending into a ready-to-produce YouTube video package, using Claude.

For each run it:

1. **Finds trending topics** across YouTube, Instagram, X/Twitter and other platforms (with live YouTube data if `YOUTUBE_API_KEY` is set).
2. **Writes an original script** for the chosen topic, then critiques and rewrites it 5 times to keep it original and copyright-safe.
3. **Picks the best narrator voice** by scoring 5 candidate voices against the script, then generates the narration audio.
4. **Writes a video-generation prompt** (shot by shot) from the script, refined 5 times.
5. **Writes a thumbnail image prompt**, reviewed and refined 5 times.
6. **Uploads everything to Google Drive** (with `--upload`).

Every output, plus every critique and revision, lands in `output/<timestamp>-<topic>/`.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,google,tts]"
cp .env.example .env   # then fill in your keys
claudeyoubot check --upload
```

## Run

```bash
# Full run with real voice and Drive upload
claudeyoubot run --niche "tech explainers" --upload

# Cheaper dry run: no TTS, no upload (still needs ANTHROPIC_API_KEY)
claudeyoubot run --silent-voice
```

## Credentials

| Variable | Needed for | Where to get it |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | Every run | console.anthropic.com |
| `YOUTUBE_API_KEY` | Optional live trending data | Google Cloud console, YouTube Data API v3 |
| `ELEVENLABS_API_KEY` | Voice (skip with `--silent-voice`) | elevenlabs.io |
| `GOOGLE_APPLICATION_CREDENTIALS` | `--upload` | Google Cloud console: OAuth client or service-account JSON with Drive API enabled |
| `GOOGLE_DRIVE_FOLDER_ID` | `--upload` | The ID at the end of the Drive folder URL (share it with the service account if you use one) |

## Tests

```bash
pytest -q
ruff check .
```

Tests use a fake LLM and a silent voice provider, so they run offline with no keys.
