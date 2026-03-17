from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    host: str = "127.0.0.1"
    port: int = 8000
    open_browser: bool = True
    db_path: Path | None = None
    db_label: str | None = None
