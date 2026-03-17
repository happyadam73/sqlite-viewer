# Demo Database

Place a small demo SQLite database at `demo/test.sqlite`.

Recommended characteristics:
- 3–5 tables
- a mix of narrow and wide tables
- enough rows to exercise vertical scrolling
- at least one table with 8+ columns to exercise horizontal scrolling
- realistic but non-sensitive sample data

Suggested usage:

```bash
python -m sqlite_browser --db demo/test.sqlite
```

This should be the default happy-path smoke test for the repo.
