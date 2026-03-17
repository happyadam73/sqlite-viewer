# SQLite Browser

A lightweight local web app for browsing SQLite files in the browser.

## Features
- open a SQLite DB by CLI path
- open a SQLite DB using a browser-native file picker
- browse tables
- expand schema/columns
- preview rows in a scrollable grid
- resizable explorer and data panes
- dark/light theme
- read-only operation

## Requirements
- Python 3.13

## Quick start

### macOS / Linux
```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m sqlite_browser --db demo/test.sqlite
```

### Windows PowerShell
```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]
python -m sqlite_browser --db demo/test.sqlite
```

## Run without a DB
```bash
python -m sqlite_browser
```

Then use the **Open SQLite file** button in the browser.

For pagination and sticky-grid smoke checks, you can also launch the richer demo fixture:

```bash
python -m sqlite_browser --db demo/gps-course.sqlite
```

## Development

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
