from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from sqlite_browser.db import (
    DEFAULT_PREVIEW_LIMIT,
    MAX_PREVIEW_LIMIT,
    DatabaseError,
    DatabaseNotLoadedError,
    get_table_rows,
    get_table_schema,
    list_tables,
)
from sqlite_browser.models import (
    ApiErrorDetail,
    ApiErrorResponse,
    AppStatus,
    TableRowsResponse,
    TableSchemaResponse,
    TablesResponse,
)

router = APIRouter(prefix="/api")


@router.get("/status", response_model=AppStatus)
def status(request: Request) -> AppStatus:
    return request.app.state.session_store.get_status()


@router.get("/tables", response_model=TablesResponse)
def tables(request: Request) -> TablesResponse | JSONResponse:
    try:
        db_path = _get_active_db_path(request)
        return TablesResponse(tables=list_tables(db_path))
    except DatabaseError as exc:
        return _error_response(exc)


@router.get("/tables/{table_name}/schema", response_model=TableSchemaResponse)
def table_schema(request: Request, table_name: str) -> TableSchemaResponse | JSONResponse:
    try:
        db_path = _get_active_db_path(request)
        return get_table_schema(db_path, table_name)
    except DatabaseError as exc:
        return _error_response(exc)


@router.get("/tables/{table_name}/rows", response_model=TableRowsResponse)
def table_rows(
    request: Request,
    table_name: str,
    limit: int = Query(DEFAULT_PREVIEW_LIMIT, ge=1, le=MAX_PREVIEW_LIMIT),
    offset: int = Query(0, ge=0),
) -> TableRowsResponse | JSONResponse:
    try:
        db_path = _get_active_db_path(request)
        return get_table_rows(db_path, table_name, limit=limit, offset=offset)
    except DatabaseError as exc:
        return _error_response(exc)


def _get_active_db_path(request: Request) -> Path:
    db_path = request.app.state.session_store.get_active_db_path()
    if db_path is None:
        raise DatabaseNotLoadedError()
    return db_path


def _error_response(exc: DatabaseError) -> JSONResponse:
    payload = ApiErrorResponse(
        error=ApiErrorDetail(code=exc.code, message=exc.message),
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())
