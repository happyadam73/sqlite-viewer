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

    rows_response = client.get("/api/tables/records/rows", params={"limit": 2, "offset": 1})
    assert rows_response.status_code == 200
    assert rows_response.json() == {
        "table_name": "records",
        "columns": ["id", "name", "score", "notes", "payload"],
        "rows": [
            [2, "Ben", 88.0, "steady", "42454e"],
            [3, "Cy", 77.25, None, "4359"],
        ],
        "limit": 2,
        "offset": 1,
    }


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
