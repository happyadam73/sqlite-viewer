# Testing Strategy

## 1. Overview

The test strategy has three layers:

1. **Unit tests with pytest**
2. **API tests with pytest**
3. **End-to-end browser tests with Playwright MCP**

The product must be built so that browser automation is reliable from the start.

## 2. Unit tests

Focus areas:
- SQLite file validation
- table discovery
- schema extraction
- row preview retrieval
- row preview pagination metadata and page-size caps
- handling of invalid DB files
- handling of missing or invalid tables
- identifier validation logic

Recommended files:
- `tests/test_db.py`

## 3. API tests

Focus areas:
- startup without DB
- startup with DB path
- status endpoint
- tables endpoint
- schema endpoint
- rows endpoint pagination parameters and metadata
- upload endpoint
- invalid upload
- no DB loaded errors

Recommended files:
- `tests/test_api.py`
- `tests/test_upload.py`

## 4. Browser tests with Playwright MCP

The app must be testable through Playwright MCP.

Required scenarios:

### Scenario 1 — empty startup
- start the app without a DB
- confirm empty state
- confirm file open button visible

### Scenario 2 — open DB with file picker
- use file chooser
- select demo DB
- confirm DB label updates
- confirm tables appear

### Scenario 3 — expand table schema
- expand a table
- confirm schema rows are visible

### Scenario 4 — select table and render rows
- click a table
- confirm title updates
- confirm grid headers and rows visible
- confirm the header row remains visible after vertical scrolling
- confirm the first column remains visible after horizontal scrolling

### Scenario 5 — paginate row previews
- use a table with more rows than the default page size
- confirm pagination controls appear
- move to the next page and confirm rows update
- change the page size and confirm the grid refreshes predictably

### Scenario 6 — theme toggle
- toggle theme
- confirm DOM class or attribute changes

### Scenario 7 — splitter drag
- drag splitter
- confirm pane size changes and app remains usable

### Scenario 8 — invalid upload
- upload invalid file
- confirm error banner
- confirm app remains stable

## 5. Testability requirements

The implementation must include:
- `data-testid` selectors
- predictable empty/loading/error states
- no flaky timing dependencies
- minimal animation on critical controls
- stable DOM structure
- stable pagination controls and scroll containers

## 6. Demo test path

The repo must include a happy-path demo flow:

```bash
python -m sqlite_browser --db demo/test.sqlite
```

This is the default manual smoke path and should also be used for quick browser testing.

## 7. Definition of done for testing

Done means:
- pytest passes locally
- manual smoke test against demo DB passes
- Playwright MCP can reliably drive the main user journey, including scrolling and paginated row browsing
