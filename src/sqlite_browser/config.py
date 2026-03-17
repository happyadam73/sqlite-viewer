from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AppConfig:
    host: str = "127.0.0.1"
    port: int = 8000
    open_browser: bool = True
