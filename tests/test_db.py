from __future__ import annotations

from pathlib import Path

import pytest

from sqlite_browser.db import (
    TableNotFoundError,
    get_table_rows,
    get_table_schema,
    list_tables,
    validate_database_file,
)


def test_validate_database_file_accepts_supported_sqlite(sample_db: Path) -> None:
    assert validate_database_file(sample_db) == sample_db.resolve()


def test_validate_database_file_rejects_unsupported_extension(tmp_path: Path) -> None:
    invalid_path = tmp_path / "not-a-db.txt"
    invalid_path.write_text("plain text", encoding="utf-8")

    with pytest.raises(Exception) as exc_info:
        validate_database_file(invalid_path)

    assert exc_info.value.code == "invalid_file_type"


def test_validate_database_file_rejects_non_sqlite_content(tmp_path: Path) -> None:
    invalid_path = tmp_path / "broken.sqlite"
    invalid_path.write_text("still not sqlite", encoding="utf-8")

    with pytest.raises(Exception) as exc_info:
        validate_database_file(invalid_path)

    assert exc_info.value.code == "invalid_sqlite_file"


def test_list_tables_returns_only_user_tables(sample_db: Path) -> None:
    tables = list_tables(sample_db)

    assert [table.name for table in tables] == ["course_summary", "records"]


def test_get_table_schema_returns_column_metadata(sample_db: Path) -> None:
    schema = get_table_schema(sample_db, "records")
    columns_by_name = {column.name: column for column in schema.columns}

    assert schema.table_name == "records"
    assert columns_by_name["id"].is_primary_key is True
    assert columns_by_name["name"].not_null is True
    assert columns_by_name["notes"].default_value == "'pending'"


def test_get_table_rows_returns_preview_rows(sample_db: Path) -> None:
    preview = get_table_rows(sample_db, "records", limit=2, offset=1)

    assert preview.table_name == "records"
    assert preview.columns == ["id", "name", "score", "notes", "payload"]
    assert preview.rows == [
        [2, "Ben", 88.0, "steady", "42454e"],
        [3, "Cy", 77.25, None, "4359"],
    ]
    assert preview.limit == 2
    assert preview.offset == 1


def test_get_table_schema_rejects_unknown_table(sample_db: Path) -> None:
    with pytest.raises(TableNotFoundError):
        get_table_schema(sample_db, "missing_table")


def test_get_table_rows_rejects_unknown_table(sample_db: Path) -> None:
    with pytest.raises(TableNotFoundError):
        get_table_rows(sample_db, "missing_table")
