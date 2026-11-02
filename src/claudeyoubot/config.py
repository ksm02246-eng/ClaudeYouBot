"""Settings loaded from environment variables (or a local .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    anthropic_model: str = "claude-opus-5-5"
    refine_rounds: int = 5
    voice_candidates: int = 5
    output_dir: str = "output"
    youtube_api_key: str | None = None
    youtube_region: str = "US"
    elevenlabs_api_key: str | None = None
    google_drive_folder_id: str | None = None
    google_credentials_file: str | None = None
    google_token_file: str = "token.json"
    extra: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> Settings:
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:  # pragma: no cover - dotenv is a declared dependency
            pass
        env = os.environ
        return cls(
            anthropic_model=env.get("CLAUDEYOUBOT_MODEL", "claude-opus-5-5"),
            refine_rounds=int(env.get("CLAUDEYOUBOT_REFINE_ROUNDS", "5")),
            voice_candidates=int(env.get("CLAUDEYOUBOT_VOICE_CANDIDATES", "5")),
            output_dir=env.get("CLAUDEYOUBOT_OUTPUT_DIR", "output"),
            youtube_api_key=env.get("YOUTUBE_API_KEY"),
            youtube_region=env.get("YOUTUBE_REGION", "US"),
            elevenlabs_api_key=env.get("ELEVENLABS_API_KEY"),
            google_drive_folder_id=env.get("GOOGLE_DRIVE_FOLDER_ID"),
            google_credentials_file=env.get("GOOGLE_APPLICATION_CREDENTIALS"),
            google_token_file=env.get("GOOGLE_TOKEN_FILE", "token.json"),
        )

    def missing_for(self, *, drive: bool, real_voice: bool) -> list[str]:
        """Names of env vars that a full (non-dry) run still needs."""
        missing = []
        if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
            missing.append("ANTHROPIC_API_KEY")
        if real_voice and not self.elevenlabs_api_key:
            missing.append("ELEVENLABS_API_KEY")
        if drive:
            if not self.google_credentials_file:
                missing.append("GOOGLE_APPLICATION_CREDENTIALS")
            if not self.google_drive_folder_id:
                missing.append("GOOGLE_DRIVE_FOLDER_ID")
        return missing
