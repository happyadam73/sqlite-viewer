# SQLite Browser

![SQLite Browser system architecture](docs/assets/architecture.png)

SQLite Browser is a lightweight local web app for inspecting SQLite files in the browser.

It is intentionally small and local-first:
- Python 3.13 backend with FastAPI
- server-rendered HTML with Jinja2
- vanilla JavaScript and plain CSS on the frontend
- standard-library `sqlite3` for database access
- read-only browsing only

You can launch it with a database path for an immediate happy path, or start with no database and open a file from the browser UI.

## What You Get

- open a SQLite DB by CLI path
- open a SQLite DB using a browser-native file picker
- browse tables in a left-hand explorer
- expand schema details for each table
- preview rows in a scrollable grid
- use pagination and page-size controls on larger tables
- resize the explorer and data panes
- switch between dark and light themes
- keep the app safe by staying read-only

## How It Works

At runtime, the app follows a small same-origin flow:

1. `sqlite-browser` or `python -m sqlite_browser` starts a local Uvicorn server.
2. The CLI builds the app configuration and optionally opens the browser to the local URL.
3. FastAPI serves `GET /`, which renders a single Jinja2 page shell plus the static CSS and JavaScript assets.
4. The frontend JavaScript calls the local JSON API to load status, tables, schema metadata, and preview rows.
5. The backend keeps track of the active database in an in-memory `SessionStore`.
6. SQLite access goes through a dedicated read-only layer that validates files, validates table names against discovered schema, and runs introspection plus paginated `SELECT` queries.
7. If the user opens a file from the browser, the backend copies it to a temp file, validates it, and promotes that temp copy to the active session database.

This keeps the product simple:
- no remote databases
- no auth
- no arbitrary SQL editor
- no write operations
- no Node or SPA build pipeline

## Core Runtime Pieces

These are the main files to read if you want to understand the implementation:

- `src/sqlite_browser/cli.py`: parses CLI args, builds config, opens the browser, and starts Uvicorn
- `src/sqlite_browser/app.py`: creates the FastAPI app, mounts static assets, registers routers, and preloads a startup DB when provided
- `src/sqlite_browser/routes/pages.py`: serves the HTML shell at `/`
- `src/sqlite_browser/routes/api.py`: serves the JSON API and the upload endpoint
- `src/sqlite_browser/session_store.py`: tracks the active database path, label, and source mode for the current local session
- `src/sqlite_browser/db.py`: validates SQLite files, opens read-only connections, discovers tables, returns schema metadata, and returns paginated row previews
- `src/sqlite_browser/templates/index.html`: defines the app shell and automation-friendly DOM structure
- `src/sqlite_browser/static/app.js`: drives the explorer, schema expansion, row grid, pagination, theme toggle, upload flow, and splitter behavior

## API Surface

The browser UI talks to a small same-origin API:

- `GET /`: render the page shell
- `GET /api/status`: return whether a database is loaded and how it was opened
- `GET /api/tables`: list available tables
- `GET /api/tables/{table_name}/schema`: return schema metadata for one table
- `GET /api/tables/{table_name}/rows?page=1&page_size=100`: return paginated preview rows
- `POST /api/open-upload`: accept a browser-selected SQLite file, validate it, and make it active

## Read-Only Safety Model

The product is deliberately read-only.

- accepted file types are limited to `.sqlite`, `.sqlite3`, and `.db`
- the backend validates that the selected file can actually be opened as SQLite
- SQLite connections are opened in read-only URI mode
- requested table names are checked against discovered tables before they are used
- the browser never receives raw filesystem access
- uploaded files are copied to temp storage instead of being used directly from the browser

## Quick Start

The primary command-line entrypoint is `sqlite-browser`.

Launch the happy-path demo flow:

```bash
sqlite-browser demo/test.sqlite
```

Start without a database:

```bash
sqlite-browser
```

Then use the **Open SQLite file** button in the browser.

For pagination and sticky-grid checks, launch the larger demo fixture:

```bash
sqlite-browser demo/gps-course.sqlite
```

## Requirements

- Python 3.13

## Install As A CLI

After installation, you can launch the app with or without a database path and it will open in your default browser.

### macOS with Homebrew Python and `pipx` (recommended)

Do not run the `pipx` install command from inside an active virtualenv.

```bash
brew install pipx
pipx ensurepath
pipx install --python python3.13 .
sqlite-browser demo/test.sqlite
```

If `sqlite-browser` is still not found after `pipx ensurepath`, open a new terminal and try again.

### Windows PowerShell with `pipx` (recommended)

```powershell
py -3.13 -m pip install --user pipx
py -3.13 -m pipx ensurepath
pipx install .
sqlite-browser demo\test.sqlite
```

### Dedicated virtualenv fallback

If you do not want to use `pipx`, install into a dedicated virtualenv instead of the system Python.

### macOS / Linux with a dedicated virtualenv

```bash
python3.13 -m venv .cli-venv
source .cli-venv/bin/activate
pip install .
sqlite-browser demo/test.sqlite
```

### Windows PowerShell with a dedicated virtualenv

```powershell
py -3.13 -m venv .cli-venv
.cli-venv\Scripts\Activate.ps1
pip install .
sqlite-browser demo\test.sqlite
```

## CLI Usage

The CLI supports:

- `sqlite-browser`
- `sqlite-browser demo/test.sqlite`
- `sqlite-browser --db demo/test.sqlite`
- `sqlite-browser -d demo/test.sqlite`
- `sqlite-browser --no-browser`
- `sqlite-browser --host 127.0.0.1 --port 8765`

`python -m sqlite_browser` still works if you prefer module execution:

```bash
python -m sqlite_browser --db demo/test.sqlite
```

## Development

### Editable install

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
sqlite-browser demo/test.sqlite
```

If the repo `.venv` is already active and you have already run `pip install -e .[dev]`, you can launch the app directly with `sqlite-browser ...`.

From the repo root, this is also a direct local-development command:

```bash
.venv/bin/sqlite-browser demo/test.sqlite
```

### Windows PowerShell editable install

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]
sqlite-browser demo\test.sqlite
```

### Make targets

Create the local virtualenv and install dependencies:

```bash
make install
```

Run tests:

```bash
make test
```

Lint:

```bash
make lint
```

Type check:

```bash
make typecheck
```

Run all checks:

```bash
make check
```

Create the local virtualenv and launch the app:

```bash
make run
```

## Demo Databases

The repo includes two demo fixtures:

- `demo/test.sqlite`: small happy-path fixture for the default smoke flow
- `demo/gps-course.sqlite`: larger fixture for pagination, sticky header, and sticky first-column checks

Recommended happy-path smoke command:

```bash
python -m sqlite_browser --db demo/test.sqlite
```

## Packaging

Build an internal-use standalone app bundle with PyInstaller:

```bash
make package
```

Smoke-test the packaged artifact, including browser launch, templates, static assets, and API startup:

```bash
make package-smoke
```

The packaged app is created under `dist/sqlite-browser/` and uses `onedir` layout for macOS- and Windows-friendly local distribution.

## Testing Approach

The repo uses three layers of verification:

- unit tests with `pytest` for DB validation and query logic
- API tests with `pytest` for startup modes, status, tables, schema, rows, and upload behavior
- browser-oriented smoke and automation flows for the main local user journey

The UI is also built with stable `data-testid` selectors, explicit loading and error states, and predictable DOM structure so browser automation stays reliable.
