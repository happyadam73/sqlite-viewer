from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from math import ceil
from pathlib import Path

from sqlite_browser.models import SchemaColumn, TableRowsResponse, TableSchemaResponse, TableSummary

SUPPORTED_EXTENSIONS = frozenset({".sqlite", ".sqlite3", ".db"})
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 500


class DatabaseError(Exception):
    """Base application error for DB-facing operations."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class DatabaseNotLoadedError(DatabaseError):
    def __init__(self) -> None:
        super().__init__(
            code="no_database_loaded",
            message="No database is currently loaded.",
            status_code=400,
        )


class InvalidDatabaseFileError(DatabaseError):
    pass


class DatabaseReadError(DatabaseError):
    def __init__(self) -> None:
        super().__init__(
            code="database_read_error",
            message="The active database could not be read.",
            status_code=500,
        )


class TableNotFoundError(DatabaseError):
    def __init__(self, table_name: str) -> None:
        super().__init__(
            code="table_not_found",
            message=f'The table "{table_name}" was not found in the active database.',
            status_code=404,
        )


def validate_database_file(db_path: Path) -> Path:
    candidate = db_path.expanduser()

    if candidate.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise InvalidDatabaseFileError(
            code="invalid_file_type",
            message="SQLite files must use a .sqlite, .sqlite3, or .db extension.",
            status_code=400,
        )

    if not candidate.exists():
        raise InvalidDatabaseFileError(
            code="database_file_not_found",
            message="The database file was not found.",
            status_code=400,
        )

    if not candidate.is_file():
        raise InvalidDatabaseFileError(
            code="invalid_database_path",
            message="The database path must point to a file.",
            status_code=400,
        )

    resolved = candidate.resolve()

    try:
        with connect_readonly(resolved) as connection:
            connection.execute("SELECT name FROM sqlite_master LIMIT 1").fetchall()
    except sqlite3.Error as exc:
        raise InvalidDatabaseFileError(
            code="invalid_sqlite_file",
            message="The selected file could not be opened as a SQLite database.",
            status_code=400,
        ) from exc

    return resolved


def list_tables(db_path: Path) -> list[TableSummary]:
    try:
        with connect_readonly(db_path) as connection:
            return _discover_tables(connection)
    except sqlite3.Error as exc:
        raise DatabaseReadError() from exc


def get_table_schema(db_path: Path, table_name: str) -> TableSchemaResponse:
    try:
        with connect_readonly(db_path) as connection:
            quoted_table_name = _require_known_table(connection, table_name)
            rows = connection.execute(f"PRAGMA table_info({quoted_table_name})").fetchall()
    except TableNotFoundError:
        raise
    except sqlite3.Error as exc:
        raise DatabaseReadError() from exc

    return TableSchemaResponse(
        table_name=table_name,
        columns=[
            SchemaColumn(
                name=row[1],
                type=row[2] or "",
                is_primary_key=bool(row[5]),
                not_null=bool(row[3]),
                default_value=_normalize_value(row[4]),
            )
            for row in rows
        ],
    )


def get_table_rows(
    db_path: Path,
    table_name: str,
    *,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> TableRowsResponse:
    bounded_page_size = min(page_size, MAX_PAGE_SIZE)
    requested_page = max(page, 1)

    try:
        with connect_readonly(db_path) as connection:
            quoted_table_name = _require_known_table(connection, table_name)
            total_rows = connection.execute(
                f"SELECT COUNT(*) FROM {quoted_table_name}"
            ).fetchone()[0]
            total_pages = max(1, ceil(total_rows / bounded_page_size)) if bounded_page_size else 1
            current_page = min(requested_page, total_pages)
            offset = (current_page - 1) * bounded_page_size
            cursor = connection.execute(
                f"SELECT * FROM {quoted_table_name} LIMIT ? OFFSET ?",
                (bounded_page_size, offset),
            )
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description or []]
    except TableNotFoundError:
        raise
    except sqlite3.Error as exc:
        raise DatabaseReadError() from exc

    return TableRowsResponse(
        table_name=table_name,
        columns=columns,
        rows=[[_normalize_value(value) for value in row] for row in rows],
        page=current_page,
        page_size=bounded_page_size,
        total_rows=total_rows,
        total_pages=total_pages,
        has_previous=current_page > 1,
        has_next=current_page < total_pages,
    )


@contextmanager
def connect_readonly(db_path: Path) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True)
    try:
        yield connection
    finally:
        connection.close()


def _discover_tables(connection: sqlite3.Connection) -> list[TableSummary]:
    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name COLLATE NOCASE
        """
    ).fetchall()
    return [TableSummary(name=row[0]) for row in rows]


def _require_known_table(connection: sqlite3.Connection, table_name: str) -> str:
    table_names = {table.name for table in _discover_tables(connection)}
    if table_name not in table_names:
        raise TableNotFoundError(table_name)
    return _quote_identifier(table_name)


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _normalize_value(value: object) -> str | int | float | bool | None:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, memoryview):
        value = value.tobytes()
    if isinstance(value, bytes):
        return value.hex()
    return str(value)
