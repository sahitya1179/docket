"""Settings, loaded from the environment (see .env.example)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    city: str = os.getenv("DOCKET_CITY", "oakland")
    cache_dir: Path = Path(os.getenv("DOCKET_CACHE_DIR", REPO_ROOT / "cache"))
    llm_cache: bool = os.getenv("DOCKET_LLM_CACHE", "1") == "1"

    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    model_triage: str = os.getenv("DOCKET_MODEL_TRIAGE", "anthropic.claude-haiku-4-5")
    model_extract: str = os.getenv("DOCKET_MODEL_EXTRACT", "anthropic.claude-haiku-4-5")
    model_brief: str = os.getenv("DOCKET_MODEL_BRIEF", "anthropic.claude-sonnet-5")

    nominatim_user_agent: str = os.getenv("NOMINATIM_USER_AGENT", "docket-hackathon/0.1")

    # PROTOCOLS.md P7 — must be True everywhere except a deliberate live deploy.
    demo_mode: bool = os.getenv("DOCKET_DEMO_MODE", "1") == "1"


settings = Settings()
