from __future__ import annotations

from contextlib import suppress
from pathlib import Path

from sqlite_browser.models import AppStatus, SourceMode


class SessionStore:
    """In-memory session state for the active database."""

    def __init__(self) -> None:
        self._db_path: Path | None = None
        self._db_label: str | None = None
        self._source_mode: SourceMode | None = None
        self._uploaded_db_path: Path | None = None

    def set_active_database(
        self,
        db_path: Path,
        *,
        label: str,
        source_mode: SourceMode,
    ) -> None:
        resolved_path = db_path.resolve()

        if source_mode == "upload":
            self._cleanup_previous_upload(except_path=resolved_path)
            self._uploaded_db_path = resolved_path
        else:
            self._cleanup_previous_upload()
            self._uploaded_db_path = None

        self._db_path = resolved_path
        self._db_label = label
        self._source_mode = source_mode

    def clear(self) -> None:
        self._cleanup_previous_upload()
        self._db_path = None
        self._db_label = None
        self._source_mode = None
        self._uploaded_db_path = None

    def get_active_db_path(self) -> Path | None:
        return self._db_path

    def get_status(self) -> AppStatus:
        return AppStatus(
            db_loaded=self._db_path is not None,
            db_label=self._db_label,
            source_mode=self._source_mode,
        )

    def _cleanup_previous_upload(self, *, except_path: Path | None = None) -> None:
        if self._uploaded_db_path is None:
            return

        if except_path is not None and self._uploaded_db_path == except_path:
            return

        with suppress(OSError):
            self._uploaded_db_path.unlink()

        self._uploaded_db_path = None
