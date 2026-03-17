from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

SourceMode = Literal["path", "upload"]


class AppStatus(BaseModel):
    db_loaded: bool
    db_label: str | None = None
    source_mode: SourceMode | None = None
