# UI / UX Specification

## 1. Layout

Single page with:
- top bar
- left explorer pane
- draggable splitter
- right data pane

## 2. Top bar

Must include:
- application title
- current DB label
- open file button
- theme toggle

Recommended:
- current DB label should show file name, optionally truncated path
- an explicit “No database loaded” label for empty state

## 3. Explorer pane

The explorer pane must:
- be scrollable vertically
- support expanding a table
- support selecting a table
- visually distinguish selected table
- show schema beneath an expanded table

Recommended visual structure:
- table row with expand icon and table name
- schema list indented beneath
- schema badges or markers for PK / NOT NULL

## 4. Data pane

The data pane must:
- show selected table title
- optionally show small metadata summary
- show grid with column headers and rows
- support both horizontal and vertical scroll

Recommended behaviour:
- sticky headers if straightforward
- monospace option not required
- long text truncated visually but inspectable via tooltip or full cell if easy

## 5. Splitter

The splitter must:
- be draggable horizontally
- preserve minimum widths on both panes
- behave consistently in dark and light themes

## 6. Themes

Support:
- light
- dark

Recommended theme behaviour:
- detect system preference on first load
- persist manual choice in local storage

## 7. States

### Empty state
Shown when no DB is loaded.
Must include:
- plain explanation
- open file call to action

### Loading state
Shown while fetching tables/schema/rows.
Must be visible and automation-friendly.

### Error state
Shown for failures such as:
- invalid DB
- unreadable DB
- failed API request

Must be prominent and easy to dismiss or replace with later success.

## 8. Accessibility and automation guidance

Key controls must have:
- obvious labels
- keyboard focus visibility where possible
- deterministic structure
- stable `data-testid` attributes

## 9. Required `data-testid` values

### App shell
- `app-shell`
- `current-db-label`
- `open-file-button`
- `theme-toggle`

### Explorer
- `explorer-pane`
- `table-list`
- `table-item-{table_name}`
- `table-expand-{table_name}`
- `schema-list-{table_name}`

### Data area
- `data-pane`
- `selected-table-title`
- `data-grid`
- `data-grid-header`
- `data-grid-body`

### States
- `empty-state`
- `error-banner`
- `loading-indicator`

### Layout
- `pane-splitter`

## 10. Playwright-friendly UI rules

The UI should avoid:
- random element IDs for key interactions
- hidden timing dependencies
- long or decorative animations on critical interactions

The UI should prefer:
- stable labels
- stable test IDs
- explicit loading indicators
- consistent selected state classes
