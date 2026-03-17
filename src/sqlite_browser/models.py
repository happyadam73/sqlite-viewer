from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

SourceMode = Literal["path", "upload"]
JsonScalar = str | int | float | bool | None


class AppStatus(BaseModel):
    db_loaded: bool
    db_label: str | None = None
    source_mode: SourceMode | None = None


class TableSummary(BaseModel):
    name: str


class TablesResponse(BaseModel):
    tables: list[TableSummary]


class OpenUploadResponse(BaseModel):
    db_loaded: bool
    db_label: str
    source_mode: SourceMode
    tables: list[TableSummary]


class SchemaColumn(BaseModel):
    name: str
    type: str
    is_primary_key: bool
    not_null: bool
    default_value: JsonScalar = None


class TableSchemaResponse(BaseModel):
    table_name: str
    columns: list[SchemaColumn]


class TableRowsResponse(BaseModel):
    table_name: str
    columns: list[str]
    rows: list[list[JsonScalar]]
    limit: int
    offset: int


class ApiErrorDetail(BaseModel):
    code: str
    message: str


class ApiErrorResponse(BaseModel):
    error: ApiErrorDetail
