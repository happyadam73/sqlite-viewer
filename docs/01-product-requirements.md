# Product Requirements Document — Local SQLite Browser

## 1. Product name

**Local SQLite Browser**

## 2. Summary

Build a lightweight local web application in Python that allows a user to inspect a SQLite database file in a browser.

The application must support two primary workflows:

1. **Launch by file path**
   - Example: `python -m sqlite_browser --db demo/test.sqlite`
   - Intended for integration with other local tools such as `smart-ingest`

2. **Open from the UI**
   - The user starts the app without a database and loads a local file via a browser-native file picker

The UI should provide:
- a left-hand explorer pane listing tables
- expandable schema/column details for each table
- a right-hand data pane showing rows for the selected table
- resizable panes
- independent scrolling
- dark and light theme support

The app is read-only and intended for local developer and data-engineering workflows.

## 3. Problem statement

SQLite files are convenient as portable single-file databases, but local inspection is often awkward:
- desktop database tools can be heavyweight
- they may not fit simple automation workflows
- they are not easy to launch directly from another CLI utility
- they may not provide the exact lightweight browser-based workflow desired for rapid validation

This project solves that by providing a simple browser-based local inspector that is easy to run, easy to automate, and focused on browsing rather than editing.

## 4. Goals

The product must:
- be quick to run locally
- be lightweight in dependency footprint
- support direct CLI launch against a DB path
- support browser-native file picking
- provide clear schema and row inspection
- be suitable for automated browser testing via Playwright MCP
- remain read-only and safe by default

## 5. Non-goals

The following are explicitly out of scope for v1:
- editing data
- editing schema
- arbitrary SQL editor
- multi-database tabbing
- remote database connections
- authentication
- collaboration or multi-user workflows
- desktop app packaging
- advanced analytics or charting

## 6. Target users

Primary users:
- developers
- data engineers
- platform engineers
- CLI tool authors
- technically confident local users inspecting SQLite outputs

## 7. Primary use cases

### Use case A — browse generated SQLite output
A user runs a CLI tool that produces a SQLite file and wants to inspect the result immediately in a browser.

### Use case B — manually inspect a local SQLite file
A user starts the browser app locally and selects a DB file using the file picker.

### Use case C — verify schemas and sample data
A user expands tables to inspect columns, clicks a table to preview its rows, and pages through larger result sets without losing header or first-column context.

## 8. Functional requirements

### 8.1 Startup modes

The application must support:

#### Mode A — no initial DB
```bash
python -m sqlite_browser
```

Expected behaviour:
- local web server starts
- browser opens unless suppressed
- app shows an empty state
- user can open a DB using the native file picker

#### Mode B — DB path provided
```bash
python -m sqlite_browser --db demo/test.sqlite
```

Expected behaviour:
- local web server starts
- browser opens unless suppressed
- DB is loaded immediately
- explorer and data panes are usable without additional steps

#### Mode C — configurable host/port
The CLI should optionally support:
```bash
python -m sqlite_browser --db demo/test.sqlite --host 127.0.0.1 --port 8765 --no-browser
```

### 8.2 File opening

The application must support opening a database by:
- command-line path argument
- browser-native file picker

Accepted file extensions:
- `.sqlite`
- `.sqlite3`
- `.db`

The app must reject invalid or unreadable files with a clear error.

### 8.3 Explorer pane

The left pane must:
- show tables from the active DB
- be vertically scrollable
- support long table names
- be user-resizable relative to the data pane
- allow each table to expand/collapse
- show schema/column metadata when expanded

Minimum schema details:
- column name
- declared type
- primary key marker
- not-null marker where available

### 8.4 Data pane

The right pane must:
- show the selected table name
- show rows for the selected table
- display column headers
- support horizontal scrolling
- support vertical scrolling
- keep column headers visible while vertically scrolling the row grid
- keep the first visible data column pinned while horizontally scrolling wide tables
- provide standard pagination controls when the current page size limit is reached
- provide a page size control as part of the pagination controls
- remain stable for wide tables and long values

For v1, the table preview may enforce a safe maximum page size such as 500.
When a table contains more rows than fit in the active page size, the UI must allow paging forward and backward through the preview data.

### 8.5 Theme support

The application must support:
- dark theme
- light theme

The app should:
- follow system theme on first load if practical
- allow manual toggle
- apply theme consistently across all panes and controls

### 8.6 States and errors

The application must handle:
- no DB loaded
- invalid file type
- unreadable file
- invalid SQLite file
- locked DB
- missing table
- backend/API failure

Errors must:
- be visible in the UI
- use plain, actionable language
- not crash the app

### 8.7 Read-only safety

The application must be read-only.
No edit, insert, update, delete, or schema-change functionality should exist in v1.

## 9. Non-functional requirements

### 9.1 Performance
- small to medium SQLite files should load quickly
- table selection should typically render within about 1 second for common preview sizes
- layout should remain responsive

### 9.2 Simplicity
- no Docker required
- no Node build pipeline required
- minimal frontend complexity
- minimal backend complexity

### 9.3 Maintainability
- clear package structure
- typed Python for core modules where practical
- tests for core behaviours
- deterministic selectors and flows for browser automation

### 9.4 Portability
The app should run on:
- macOS
- Windows
- Linux

using Python 3.13 and a local `.venv`.

## 10. Success criteria

The product is successful when a user can:
- start it locally in a fresh `.venv`
- load a DB by path or by file picker
- browse tables and schema
- preview rows in a scrollable, paginated grid without losing headers or first-column context
- resize the layout
- switch theme
- run reliable automated UI tests through Playwright MCP

## 11. Acceptance criteria

The project is done when:
- the app starts locally with Python 3.13
- the app supports both startup modes
- the file picker works
- tables and schema load correctly
- rows display correctly with sticky headers, a sticky first column, and pagination when needed
- panes are resizable and scroll independently
- dark/light themes work
- invalid file handling is clear and stable
- pytest test suite passes
- Playwright MCP scenarios pass
- the demo DB can be launched from a happy-path command
