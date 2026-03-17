from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from sqlite_browser.app import create_app
from sqlite_browser.config import AppConfig


def test_status_without_database_loaded() -> None:
    client = TestClient(create_app())

    response = client.get("/api/status")

    assert response.status_code == 200
    assert response.json() == {
        "db_loaded": False,
        "db_label": None,
        "source_mode": None,
    }


def test_tables_endpoint_requires_database() -> None:
    client = TestClient(create_app())

    response = client.get("/api/tables")

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "no_database_loaded",
            "message": "No database is currently loaded.",
        }
    }


def test_milestone_two_api_happy_path(sample_db: Path) -> None:
    client = TestClient(
        create_app(
            config=AppConfig(
                db_path=sample_db,
                db_label="demo/test.sqlite",
            )
        )
    )

    status_response = client.get("/api/status")
    assert status_response.status_code == 200
    assert status_response.json() == {
        "db_loaded": True,
        "db_label": "demo/test.sqlite",
        "source_mode": "path",
    }

    tables_response = client.get("/api/tables")
    assert tables_response.status_code == 200
    assert tables_response.json() == {
        "tables": [
            {"name": "course_summary"},
            {"name": "records"},
        ]
    }

    schema_response = client.get("/api/tables/records/schema")
    assert schema_response.status_code == 200
    assert schema_response.json() == {
        "table_name": "records",
        "columns": [
            {
                "name": "id",
                "type": "INTEGER",
                "is_primary_key": True,
                "not_null": False,
                "default_value": None,
            },
            {
                "name": "name",
                "type": "TEXT",
                "is_primary_key": False,
                "not_null": True,
                "default_value": None,
            },
            {
                "name": "score",
                "type": "REAL",
                "is_primary_key": False,
                "not_null": False,
                "default_value": None,
            },
            {
                "name": "notes",
                "type": "TEXT",
                "is_primary_key": False,
                "not_null": False,
                "default_value": "'pending'",
            },
            {
                "name": "payload",
                "type": "BLOB",
                "is_primary_key": False,
                "not_null": False,
                "default_value": None,
            },
        ],
    }

    rows_response = client.get("/api/tables/records/rows", params={"page": 2, "page_size": 2})
    assert rows_response.status_code == 200
    assert rows_response.json() == {
        "table_name": "records",
        "columns": ["id", "name", "score", "notes", "payload"],
        "rows": [[3, "Cy", 77.25, None, "4359"]],
        "page": 2,
        "page_size": 2,
        "total_rows": 3,
        "total_pages": 2,
        "has_previous": True,
        "has_next": False,
    }


def test_startup_with_repo_gps_course_database_supports_paginated_rows(
    gps_course_db_path: Path,
) -> None:
    client = TestClient(
        create_app(
            config=AppConfig(
                db_path=gps_course_db_path,
                db_label="demo/gps-course.sqlite",
            )
        )
    )

    status_response = client.get("/api/status")
    assert status_response.status_code == 200
    assert status_response.json() == {
        "db_loaded": True,
        "db_label": "demo/gps-course.sqlite",
        "source_mode": "path",
    }

    tables_response = client.get("/api/tables")
    assert tables_response.status_code == 200
    assert tables_response.json() == {
        "tables": [
            {"name": "course_points"},
            {"name": "course_summary"},
            {"name": "records"},
        ]
    }

    rows_response = client.get("/api/tables/records/rows", params={"page": 2, "page_size": 100})
    assert rows_response.status_code == 200
    payload = rows_response.json()
    assert payload["table_name"] == "records"
    assert payload["columns"] == [
        "id",
        "timestamp",
        "distance_m",
        "position_lat",
        "position_long",
        "altitude_m",
    ]
    assert payload["page"] == 2
    assert payload["page_size"] == 100
    assert payload["total_rows"] == 2169
    assert payload["total_pages"] == 22
    assert payload["has_previous"] is True
    assert payload["has_next"] is True
    assert len(payload["rows"]) == 100
    assert payload["rows"][0] == [101, "2024-08-16T00:09:34", 4145.2, 51.2134509, -2.774414, 13.0]
    assert payload["rows"][-1] == [200, "2024-08-16T00:20:46", 8374.23, 51.2052679, -2.7199429, 20.0]


def test_invalid_table_returns_404(sample_db: Path) -> None:
    client = TestClient(create_app(config=AppConfig(db_path=sample_db, db_label="demo/test.sqlite")))

    response = client.get("/api/tables/missing_table/schema")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "table_not_found",
            "message": 'The table "missing_table" was not found in the active database.',
        }
    }


def test_invalid_table_rows_returns_404(sample_db: Path) -> None:
    client = TestClient(create_app(config=AppConfig(db_path=sample_db, db_label="demo/test.sqlite")))

    response = client.get("/api/tables/missing_table/rows")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "table_not_found",
            "message": 'The table "missing_table" was not found in the active database.',
        }
    }


def test_rows_endpoint_rejects_invalid_pagination_values(sample_db: Path) -> None:
    client = TestClient(create_app(config=AppConfig(db_path=sample_db, db_label="demo/test.sqlite")))

    response = client.get("/api/tables/records/rows", params={"page": 0, "page_size": 0})

    assert response.status_code == 422


def test_open_upload_loads_database_and_updates_session(sample_db: Path) -> None:
    client = TestClient(create_app())

    with sample_db.open("rb") as uploaded_file:
        response = client.post(
            "/api/open-upload",
            files={"file": ("uploaded.sqlite", uploaded_file, "application/octet-stream")},
        )

    assert response.status_code == 200
    assert response.json() == {
        "db_loaded": True,
        "db_label": "uploaded.sqlite",
        "source_mode": "upload",
        "tables": [
            {"name": "course_summary"},
            {"name": "records"},
        ],
    }

    status_response = client.get("/api/status")
    assert status_response.status_code == 200
    assert status_response.json() == {
        "db_loaded": True,
        "db_label": "uploaded.sqlite",
        "source_mode": "upload",
    }

    tables_response = client.get("/api/tables")
    assert tables_response.status_code == 200
    assert tables_response.json() == {
        "tables": [
            {"name": "course_summary"},
            {"name": "records"},
        ]
    }


def test_invalid_upload_preserves_last_known_good_database(sample_db: Path) -> None:
    client = TestClient(
        create_app(
            config=AppConfig(
                db_path=sample_db,
                db_label="demo/test.sqlite",
            )
        )
    )

    response = client.post(
        "/api/open-upload",
        files={"file": ("broken.sqlite", b"not a sqlite database", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "invalid_sqlite_file",
            "message": "The selected file could not be opened as a SQLite database.",
        }
    }

    status_response = client.get("/api/status")
    assert status_response.status_code == 200
    assert status_response.json() == {
        "db_loaded": True,
        "db_label": "demo/test.sqlite",
        "source_mode": "path",
    }

    tables_response = client.get("/api/tables")
    assert tables_response.status_code == 200
    assert tables_response.json() == {
        "tables": [
            {"name": "course_summary"},
            {"name": "records"},
        ]
    }
