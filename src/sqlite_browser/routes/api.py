from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Query, Request, UploadFile
from fastapi.responses import JSONResponse

from sqlite_browser.db import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    DatabaseError,
    DatabaseNotLoadedError,
    get_table_rows,
    get_table_schema,
    list_tables,
    validate_database_file,
)
from sqlite_browser.models import (
    ApiErrorDetail,
    ApiErrorResponse,
    AppStatus,
    OpenUploadResponse,
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
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> TableRowsResponse | JSONResponse:
    try:
        db_path = _get_active_db_path(request)
        return get_table_rows(db_path, table_name, page=page, page_size=page_size)
    except DatabaseError as exc:
        return _error_response(exc)


@router.post("/open-upload", response_model=OpenUploadResponse)
async def open_upload(
    request: Request,
    file: UploadFile | None = File(default=None),
) -> OpenUploadResponse | JSONResponse:
    uploaded_file = file
    temp_path: Path | None = None

    try:
        if uploaded_file is None or not uploaded_file.filename:
            raise DatabaseError(
                code="missing_upload_file",
                message="Choose a SQLite file to open.",
                status_code=400,
            )

        upload_name = Path(uploaded_file.filename).name
        temp_path = _copy_upload_to_temp(uploaded_file, upload_name)
        validated_path = validate_database_file(temp_path)
        tables = list_tables(validated_path)
        request.app.state.session_store.set_active_database(
            validated_path,
            label=upload_name,
            source_mode="upload",
        )
        return OpenUploadResponse(
            db_loaded=True,
            db_label=upload_name,
            source_mode="upload",
            tables=tables,
        )
    except DatabaseError as exc:
        _remove_temp_file(temp_path)
        return _error_response(exc)
    finally:
        if file is not None:
            await file.close()


def _get_active_db_path(request: Request) -> Path:
    db_path = request.app.state.session_store.get_active_db_path()
    if db_path is None:
        raise DatabaseNotLoadedError()
    return db_path


def _copy_upload_to_temp(file: UploadFile, upload_name: str) -> Path:
    suffix = Path(upload_name).suffix
    file_descriptor, raw_path = tempfile.mkstemp(prefix="sqlite-browser-", suffix=suffix)
    temp_path = Path(raw_path)

    try:
        with open(file_descriptor, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
    except OSError as exc:
        _remove_temp_file(temp_path)
        raise DatabaseError(
            code="upload_storage_failed",
            message="The selected file could not be stored for browsing.",
            status_code=500,
        ) from exc

    return temp_path


def _remove_temp_file(temp_path: Path | None) -> None:
    if temp_path is None:
        return

    try:
        temp_path.unlink()
    except FileNotFoundError:
        return
    except OSError:
        return


def _error_response(exc: DatabaseError) -> JSONResponse:
    payload = ApiErrorResponse(
        error=ApiErrorDetail(code=exc.code, message=exc.message),
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())
