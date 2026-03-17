# Execution Plan

This plan is derived from the product, architecture, API, UI, testing, and delivery documents in `docs/`.
When implementing from a minimal prompt, work milestone by milestone and keep changes aligned with the current repo specs.
When a checklist task is completed and verified, mark it done by changing `- [ ]` to `- [x]`.

## Milestone 1 - Scaffold The App Shell

- [x] Create the `src/sqlite_browser/` package and the baseline module layout described in `docs/00-repo-structure.md`.
- [x] Implement the FastAPI app factory, router registration, and server-rendered `GET /` page shell.
- [x] Add the CLI entry point for `python -m sqlite_browser` and the `sqlite-browser` console script path.
- [x] Add the base Jinja template and static CSS/JS assets for the single-page shell.
- [x] Render the empty state, top bar, explorer pane, data pane, and required `data-testid` attributes for the shell.
- [x] Verify the app starts locally and the empty state is visible without a database loaded.

## Milestone 2 - Read-Only SQLite Core And CLI DB Loading

- [x] Implement SQLite file validation for supported extensions: `.sqlite`, `.sqlite3`, and `.db`.
- [x] Implement read-only connection handling with safe table discovery, schema inspection, and row preview queries.
- [x] Add session state for the active database label and source mode for startup via `--db`.
- [x] Support CLI options for `--db`, `--host`, `--port`, and `--no-browser` with loopback defaults.
- [x] Add `GET /api/status`, `GET /api/tables`, `GET /api/tables/{table_name}/schema`, and `GET /api/tables/{table_name}/rows`.
- [x] Verify the happy path `python -m sqlite_browser --db demo/test.sqlite` loads tables and row previews.

## Milestone 3 - Explorer And Data Grid Interaction

- [x] Implement frontend loading of app status, tables, schema details, and row previews from the JSON API.
- [x] Render expandable table items in the explorer and display schema metadata including PK and NOT NULL markers.
- [x] Render the selected table title, column headers, and preview rows in a scrollable data grid.
- [x] Validate requested table names against discovered schema before any schema or row query is executed.
- [x] Add clear empty, loading, and backend error states that do not crash the app.
- [x] Verify table expansion and table selection work reliably from a fresh page load.

## Milestone 4 - Browser Upload Flow

- [x] Add the browser-native file picker flow behind the `open-file-button` control.
- [x] Implement `POST /api/open-upload` with multipart handling, temp-copy storage, and active-session replacement.
- [x] Preserve the last known good state when an upload fails validation or cannot be opened as SQLite.
- [x] Return consistent API error payloads with stable error codes and actionable messages.
- [x] Update the UI after successful upload to refresh the DB label, source mode, tables, and selected-table state.
- [x] Verify a user can start with no DB, upload `demo/test.sqlite`, and browse without restarting the app.

## Milestone 5 - UX Polish And Theming

- [x] Implement the draggable horizontal splitter with minimum pane widths and stable behaviour in both themes.
- [x] Add independent scrolling for the explorer pane and data pane, including wide-table horizontal overflow.
- [x] Extend the rows API and frontend state to support paginated table previews with bounded page-size options and deterministic pagination metadata.
- [x] Keep grid column headers visible during vertical scrolling and keep the first column visible during horizontal scrolling.
- [x] Add standard pagination controls with previous/next navigation and a page-size selector when the selected table exceeds the active page size.
- [x] Implement dark and light themes, follow system preference on first load if practical, and persist manual choice locally.
- [x] Improve selected-table styling and prominent error-banner presentation without regressing the sticky grid and pagination behaviour.
- [x] Keep key interactions automation-friendly by avoiding flaky timing dependencies and heavy animations.
- [x] Verify the primary browsing workflow remains stable across empty, loading, success, error, tall-table, wide-table, and paginated-table states.

## Milestone 6 - Tests, Demo Data, And Release Readiness

- [x] Maintain representative demo fixtures at `demo/test.sqlite` and `demo/gps-course.sqlite`, plus supporting demo notes for smoke testing and pagination/sticky-grid scenarios.
- [x] Add pytest unit coverage for DB validation, table discovery, schema extraction, paginated row preview logic, and invalid-table handling.
- [x] Add pytest API coverage for startup modes, status, tables, schema, paginated rows, upload, and no-DB error cases.
- [x] Ensure the UI exposes the required `data-testid` selectors for Playwright-driven scenarios.
- [x] Run and fix `pytest`, `ruff check .`, and `mypy src` for the implemented codebase.
- [x] Perform the manual smoke path and the required Playwright scenarios for empty startup, upload, schema expand, sticky-header row browsing, pagination/page-size controls using `demo/gps-course.sqlite`, theme toggle, splitter drag, and invalid upload.

## Milestone 7 - Cross-Platform CLI Packaging And UX

- [x] Support `sqlite-browser [db_path]` while keeping `--db` and adding `-d` as compatible DB-path options.
- [x] Keep the DB path inputs unambiguous by rejecting simultaneous positional and flag-based DB arguments.
- [x] Extract browser launch URL handling so wildcard bind hosts open a loopback URL in the user's default browser.
- [x] Update the README to document `sqlite-browser` as the primary CLI, with `pipx` and `pip install` user flows for macOS and Windows.
- [x] Add an internal-use standalone packaging track with PyInstaller in `onedir` mode.
- [x] Add automated verification for the expanded CLI surface and a packaged-artifact smoke check.
