# Architecture Specification

## 1. Architecture overview

This application should use a lightweight server-rendered architecture:

- **Backend**: FastAPI
- **Templating**: Jinja2
- **Frontend**: vanilla JavaScript + plain CSS
- **Database access**: Python `sqlite3`
- **Testing**: pytest + Playwright MCP

This avoids the complexity of a separate SPA build pipeline while still providing a responsive local UI.

## 2. High-level components

### Backend
Responsibilities:
- start local HTTP server
- accept optional DB path on startup
- accept file upload via browser picker
- validate SQLite files
- open database in read-only mode where practical
- enumerate tables
- fetch schema metadata
- fetch row previews
- expose API endpoints used by the UI

### Frontend
Responsibilities:
- render the split-pane page
- handle file picker interactions
- request and render tables/schema/rows
- manage selected table state
- manage theme toggle
- manage splitter drag behaviour
- display loading, empty, and error states

### Session store
Needed to track the currently active DB for the local app session, especially when a file is uploaded through the UI.

This can be simple and local:
- in-memory session registry
- temporary file path storage for uploaded DB copies

## 3. Recommended runtime model

### DB opened by CLI path
The backend receives `--db path/to/file.sqlite` at startup and uses it directly.

### DB opened by file picker
The browser uploads a selected file to the backend.
The backend:
- validates it
- stores a temp copy for the session
- marks that temp copy as the active DB
- opens it read-only for browsing

## 4. Read-only data access strategy

Preferred:
- open SQLite using a read-only URI mode where feasible
- do not expose write paths in code or UI
- use only introspection and select statements

Examples of access patterns:
- discover tables from `sqlite_master`
- retrieve columns from `PRAGMA table_info`
- retrieve rows using `SELECT * ... LIMIT ... OFFSET ...`

## 5. Data model concepts

Minimal response models:

### App status
- current DB loaded or not
- file name / display label
- file source mode: path or upload

### Table summary
- table name

### Schema column
- name
- type
- is_primary_key
- not_null
- default_value if useful

### Row preview
- column names
- array of row objects or arrays
- row limit metadata

## 6. Backend module responsibilities

### `app.py`
Application factory and router registration

### `cli.py`
Command-line parsing and server launch

### `db.py`
All SQLite-specific logic:
- validate file
- open DB connection
- discover tables
- fetch schema
- fetch rows

### `session_store.py`
Track current active DB and temp upload lifecycle

### `routes/pages.py`
Serve the HTML shell

### `routes/api.py`
Serve JSON and file-upload endpoints

### `models.py`
Pydantic models for API responses

## 7. Security considerations

Although local-only, still apply discipline:
- validate table names against actual discovered tables before composing SQL identifiers
- do not expose arbitrary filesystem browsing
- bind to loopback by default
- avoid persisting uploaded DBs beyond session need
- reject unsafe or malformed requests clearly

## 8. Why not React or a heavier frontend?

Not needed for v1.
This product benefits more from:
- fast startup
- less complexity
- easier agentic coding
- easier local maintenance
- fewer moving parts for Playwright automation
