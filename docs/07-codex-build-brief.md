# Codex Build Brief

Build a lightweight Python 3.13 local web app for browsing SQLite files in the browser. Use FastAPI for the backend, Jinja2 templates for server-rendered HTML, vanilla JavaScript for interactivity, plain CSS for styling, and Python’s standard `sqlite3` for DB access. The UI must be a single page with a resizable left explorer pane listing tables and expandable schema/columns, plus a resizable right pane showing selected table rows in a grid with both horizontal and vertical scrolling. The app must support two open modes: launching directly with `--db path/to/file.sqlite`, and opening a local file via a browser-native file picker that uploads the DB to the backend. Keep the app read-only, local-only, and low-dependency. Support dark and light themes. Include stable `data-testid` selectors from day one so Playwright MCP can test empty state, file open, schema expand, row browsing, theme toggle, splitter drag, and invalid file handling. Add a demo DB under `demo/test.sqlite` and ensure the happy path `python -m sqlite_browser --db demo/test.sqlite` works cleanly.

## Additional build instructions

### Project/runtime requirements
- Python 3.13
- local `.venv` in repo root
- no Poetry required
- use pytest, ruff, mypy
- no React, no Vite, no Node build chain required for the app UI

### Expected CLI
Support:
```bash
python -m sqlite_browser
python -m sqlite_browser --db demo/test.sqlite
python -m sqlite_browser --db demo/test.sqlite --port 8765
python -m sqlite_browser --db demo/test.sqlite --no-browser
```

### Required endpoints
- `GET /`
- `GET /api/status`
- `GET /api/tables`
- `GET /api/tables/{table_name}/schema`
- `GET /api/tables/{table_name}/rows`
- `POST /api/open-upload`

### Required test IDs
- `app-shell`
- `open-file-button`
- `theme-toggle`
- `current-db-label`
- `explorer-pane`
- `table-list`
- `table-item-{table_name}`
- `table-expand-{table_name}`
- `schema-list-{table_name}`
- `data-pane`
- `selected-table-title`
- `data-grid`
- `data-grid-header`
- `data-grid-body`
- `pane-splitter`
- `empty-state`
- `error-banner`
- `loading-indicator`

### Required tests
- pytest unit tests for DB logic
- pytest API tests
- manual/demo smoke path
- implementation designed to be exercised by Playwright MCP

### Constraints
- read-only only
- local-only host by default
- stable selectors
- simple maintainable structure
- avoid unnecessary framework complexity
