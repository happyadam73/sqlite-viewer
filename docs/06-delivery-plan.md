# Delivery Plan

## 1. Delivery approach

Build in small, verifiable increments.

## 2. Milestones

## Milestone 1 — repo scaffold
Deliver:
- Python 3.13 project structure
- `pyproject.toml`
- FastAPI app shell
- Jinja template
- static CSS/JS
- CLI entry point
- `.venv`-friendly setup
- README with local run steps

Exit criteria:
- app starts
- browser loads shell page
- empty state visible

## Milestone 2 — DB by path
Deliver:
- `--db` CLI support
- DB validation
- active DB session state
- tables endpoint
- schema endpoint
- rows endpoint

Exit criteria:
- demo DB loads from CLI path
- tables and rows visible in browser

## Milestone 3 — explorer and data grid
Deliver:
- frontend loading for status, tables, schema, and rows
- expandable table schema in the explorer
- selected-table title and row grid rendering
- empty, loading, and error states for table browsing

Exit criteria:
- table expansion and selection work from a fresh page load

## Milestone 4 — browser upload flow
Deliver:
- open file button
- browser-native file input
- upload endpoint
- temp file handling
- UI refresh after upload

Exit criteria:
- user can open a DB without restarting the app

## Milestone 5 — UX polish and theming
Deliver:
- resizable panes
- independent scrolling
- selected-table state
- sticky column headers during vertical grid scroll
- sticky first column during horizontal grid scroll
- standard pagination controls with page size selector for large tables
- better empty/loading/error states
- theme toggle with persistence

Exit criteria:
- primary workflow feels stable and usable across tall, wide, and paginated tables

## Milestone 6 — tests
Deliver:
- pytest unit tests
- pytest API tests
- Playwright-friendly DOM/test IDs
- documented browser smoke flow

Exit criteria:
- tests pass
- app is ready for agentic iteration

## 3. Risks and mitigations

### Risk: browser file path access assumptions
Mitigation:
- use upload flow, not raw local path from the browser

### Risk: flaky browser automation
Mitigation:
- stable `data-testid`
- simple DOM
- explicit loading/error states

### Risk: unsafe table name interpolation
Mitigation:
- validate requested table names against discovered schema before querying

### Risk: wide tables breaking layout
Mitigation:
- explicit overflow handling
- fixed layout rules
- horizontal scrolling in data pane
- sticky first-column treatment that preserves readability during horizontal scroll

### Risk: large row previews becoming hard to browse
Mitigation:
- enforce bounded page sizes
- expose deterministic pagination controls
- return pagination metadata from the rows API

## 4. Priority order

Implementation order:
1. scaffold app
2. CLI DB loading
3. explorer and grid UI
4. file upload flow
5. theme support and grid polish
6. pagination and sticky grid behaviour
7. pane resize
8. tests and release readiness
