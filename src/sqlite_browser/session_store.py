from __future__ import annotations

from sqlite_browser.models import AppStatus, SourceMode


class SessionStore:
    """In-memory session state for the active database."""

    def __init__(self) -> None:
        self._db_label: str | None = None
        self._source_mode: SourceMode | None = None

    def get_status(self) -> AppStatus:
        return AppStatus(
            db_loaded=self._db_label is not None,
            db_label=self._db_label,
            source_mode=self._source_mode,
        )
