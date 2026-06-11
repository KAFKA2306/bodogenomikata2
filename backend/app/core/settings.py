import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


def load_config() -> dict[str, Any]:
    root: Path = Path(os.getenv("LAMBDA_TASK_ROOT", Path(__file__).resolve().parent.parent.parent.parent))
    possible_paths: list[Path] = [
        root / "config.yaml",
        root / "backend" / "config.yaml",
    ]
    for config_path in possible_paths:
        if config_path.exists():
            with open(config_path) as f:
                data: Any = yaml.safe_load(f)
                return data if isinstance(data, dict) else {}
    return {}


_config: dict[str, Any] = load_config()
_root: Path = Path(os.getenv("LAMBDA_TASK_ROOT", Path(__file__).resolve().parent.parent.parent.parent))
load_dotenv(_root / ".env")

CANONICAL_GEMINI_MODEL: str = "gemini-2.5-flash"


class Settings:
    def __init__(self) -> None:
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY") or str(_config.get("gemini_api_key") or "")
        self.gemini_model: str = os.getenv("GEMINI_MODEL") or str(_config.get("gemini_model") or CANONICAL_GEMINI_MODEL)
        self.bgg_access_token: str = os.getenv("BGG_ACCESS_TOKEN") or str(_config.get("bgg_access_token") or "")


settings: Settings = Settings()
