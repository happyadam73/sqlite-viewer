# API Specification

## 1. Overview

The frontend should interact with a small set of JSON APIs and one file-upload endpoint.

All APIs are local and same-origin.

## 2. Endpoints

## `GET /`
Returns the main HTML page.

## `GET /api/status`
Returns app status.

Example response:
```json
{
  "db_loaded": true,
  "db_label": "demo/test.sqlite",
  "source_mode": "path"
}
```

## `GET /api/tables`
Returns available tables.

Example response:
```json
{
  "tables": [
    {"name": "course_points"},
    {"name": "course_summary"},
    {"name": "records"}
  ]
}
```

## `GET /api/tables/{table_name}/schema`
Returns schema metadata for a table.

Example response:
```json
{
  "table_name": "course_points",
  "columns": [
    {
      "name": "id",
      "type": "INTEGER",
      "is_primary_key": true,
      "not_null": false
    },
    {
      "name": "name",
      "type": "TEXT",
      "is_primary_key": false,
      "not_null": false
    }
  ]
}
```

## `GET /api/tables/{table_name}/rows?limit=500&offset=0`
Returns table preview rows.

Example response:
```json
{
  "table_name": "course_points",
  "columns": ["id", "name", "type", "timestamp"],
  "rows": [
    [1, "Start here", "generic", "2024-08-16T00:00:00"],
    [2, "300ft:Turn", "left", "2024-08-16T00:00:00"]
  ],
  "limit": 500,
  "offset": 0
}
```

## `POST /api/open-upload`
Accepts multipart upload of a SQLite file selected from the file picker.

Responsibilities:
- validate extension
- validate SQLite readability
- store a temp copy
- make it the active DB
- return updated DB status and tables

Possible success response:
```json
{
  "db_loaded": true,
  "db_label": "test.sqlite",
  "source_mode": "upload",
  "tables": [
    {"name": "course_points"},
    {"name": "course_summary"}
  ]
}
```

## 3. Error response format

Use a consistent error shape:
```json
{
  "error": {
    "code": "invalid_sqlite_file",
    "message": "The selected file could not be opened as a SQLite database."
  }
}
```

## 4. Validation rules

### Table names
Must be validated against actual discovered tables before use.
Do not trust arbitrary path parameters as safe SQL identifiers.

### Limits
Apply sensible caps to row limit requests to prevent abuse or accidental overload.

## 5. Behavioural rules

- if no DB is loaded, APIs that require a DB should return a clear error
- if an invalid table is requested, return a 404 or equivalent application error
- if upload fails, preserve prior good state where practical
