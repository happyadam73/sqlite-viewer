# Demo Databases

The repo ships with two demo SQLite files:

- `demo/test.sqlite`
  - Small happy-path fixture for the default smoke flow.
  - Includes a mix of narrow and wider tables plus a compact audit table.
- `demo/gps-course.sqlite`
  - Larger real-world style fixture for pagination, sticky header, and sticky first-column checks.
  - Includes `records` with 2,169 rows and `course_points` with 111 rows.

Recommended smoke usage:

```bash
python -m sqlite_browser --db demo/test.sqlite
```

Use `demo/test.sqlite` for the default happy-path smoke test for the repo.

Use the richer GPS fixture when you need to verify release-readiness scenarios that depend on larger datasets:

```bash
python -m sqlite_browser --db demo/gps-course.sqlite
```

Recommended Milestone 6 checks with `demo/gps-course.sqlite`:
- browse `records` to confirm pagination controls and page-size changes
- scroll the grid to confirm the sticky header remains visible
- scroll horizontally to confirm the first column remains visible
- expand `course_points` to confirm schema rendering remains stable on the larger fixture
