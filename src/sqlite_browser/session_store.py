from __future__ import annotations

from pathlib import Path

from sqlite_browser.models import AppStatus, SourceMode


class SessionStore:
    """In-memory session state for the active database."""

    def __init__(self) -> None:
        self._db_path: Path | None = None
        self._db_label: str | None = None
        self._source_mode: SourceMode | None = None

    def set_active_database(
        self,
        db_path: Path,
        *,
        label: str,
        source_mode: SourceMode,
    ) -> None:
        self._db_path = db_path.resolve()
        self._db_label = label
        self._source_mode = source_mode

    def clear(self) -> None:
        self._db_path = None
        self._db_label = None
        self._source_mode = None

    def get_active_db_path(self) -> Path | None:
        return self._db_path

    def get_status(self) -> AppStatus:
        return AppStatus(
            db_loaded=self._db_path is not None,
            db_label=self._db_label,
            source_mode=self._source_mode,
        )
