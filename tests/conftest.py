from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
REPO_ROOT = Path(__file__).resolve().parents[1]

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture(scope="session")
def demo_test_db_path() -> Path:
    return REPO_ROOT / "demo" / "test.sqlite"


@pytest.fixture(scope="session")
def gps_course_db_path() -> Path:
    return REPO_ROOT / "demo" / "gps-course.sqlite"


@pytest.fixture
def sample_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "sample.sqlite"
    connection = sqlite3.connect(db_path)
    connection.executescript(
        """
        CREATE TABLE records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score REAL,
            notes TEXT DEFAULT 'pending',
            payload BLOB
        );

        CREATE TABLE course_summary (
            course_name TEXT PRIMARY KEY,
            total_points INTEGER NOT NULL
        );
        """
    )
    connection.executemany(
        "INSERT INTO records (name, score, notes, payload) VALUES (?, ?, ?, ?)",
        [
            ("Ada", 98.5, "top of class", bytes.fromhex("414441")),
            ("Ben", 88.0, "steady", bytes.fromhex("42454E")),
            ("Cy", 77.25, None, bytes.fromhex("4359")),
        ],
    )
    connection.executemany(
        "INSERT INTO course_summary (course_name, total_points) VALUES (?, ?)",
        [
            ("SQL 101", 120),
            ("SQLite Deep Dive", 240),
        ],
    )
    connection.commit()
    connection.close()
    return db_path
