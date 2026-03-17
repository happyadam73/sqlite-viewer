from __future__ import annotations

from pathlib import Path

import pytest

from sqlite_browser.db import (
    MAX_PAGE_SIZE,
    TableNotFoundError,
    get_table_rows,
    get_table_schema,
    list_tables,
    validate_database_file,
)


def test_validate_database_file_accepts_supported_sqlite(sample_db: Path) -> None:
    assert validate_database_file(sample_db) == sample_db.resolve()


@pytest.mark.parametrize("fixture_name", ["demo_test_db_path", "gps_course_db_path"])
def test_validate_database_file_accepts_repo_demo_databases(
    fixture_name: str,
    request: pytest.FixtureRequest,
) -> None:
    db_path = request.getfixturevalue(fixture_name)

    assert validate_database_file(db_path) == db_path.resolve()


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


def test_list_tables_returns_expected_gps_course_tables(gps_course_db_path: Path) -> None:
    tables = list_tables(gps_course_db_path)

    assert [table.name for table in tables] == ["course_points", "course_summary", "records"]


def test_get_table_schema_returns_column_metadata(sample_db: Path) -> None:
    schema = get_table_schema(sample_db, "records")
    columns_by_name = {column.name: column for column in schema.columns}

    assert schema.table_name == "records"
    assert columns_by_name["id"].is_primary_key is True
    assert columns_by_name["name"].not_null is True
    assert columns_by_name["notes"].default_value == "'pending'"


def test_get_table_rows_returns_preview_rows(sample_db: Path) -> None:
    preview = get_table_rows(sample_db, "records", page=2, page_size=2)

    assert preview.table_name == "records"
    assert preview.columns == ["id", "name", "score", "notes", "payload"]
    assert preview.rows == [[3, "Cy", 77.25, None, "4359"]]
    assert preview.page == 2
    assert preview.page_size == 2
    assert preview.total_rows == 3
    assert preview.total_pages == 2
    assert preview.has_previous is True
    assert preview.has_next is False


def test_get_table_rows_supports_repo_demo_pagination(gps_course_db_path: Path) -> None:
    preview = get_table_rows(gps_course_db_path, "records", page=2, page_size=100)

    assert preview.table_name == "records"
    assert preview.columns == [
        "id",
        "timestamp",
        "distance_m",
        "position_lat",
        "position_long",
        "altitude_m",
    ]
    assert len(preview.rows) == 100
    assert preview.rows[0] == [101, "2024-08-16T00:09:34", 4145.2, 51.2134509, -2.774414, 13.0]
    assert preview.rows[-1] == [200, "2024-08-16T00:20:46", 8374.23, 51.2052679, -2.7199429, 20.0]
    assert preview.page == 2
    assert preview.page_size == 100
    assert preview.total_rows == 2169
    assert preview.total_pages == 22
    assert preview.has_previous is True
    assert preview.has_next is True


def test_get_table_rows_caps_requested_page_size(sample_db: Path) -> None:
    preview = get_table_rows(sample_db, "records", page=1, page_size=MAX_PAGE_SIZE + 100)

    assert preview.page == 1
    assert preview.page_size == MAX_PAGE_SIZE
    assert preview.total_rows == 3
    assert preview.total_pages == 1
    assert preview.has_previous is False
    assert preview.has_next is False


def test_get_table_rows_clamps_requested_page_to_last_page(sample_db: Path) -> None:
    preview = get_table_rows(sample_db, "records", page=9, page_size=2)

    assert preview.page == 2
    assert preview.page_size == 2
    assert preview.rows == [[3, "Cy", 77.25, None, "4359"]]


def test_get_table_schema_rejects_unknown_table(sample_db: Path) -> None:
    with pytest.raises(TableNotFoundError):
        get_table_schema(sample_db, "missing_table")


def test_get_table_rows_rejects_unknown_table(sample_db: Path) -> None:
    with pytest.raises(TableNotFoundError):
        get_table_rows(sample_db, "missing_table")
