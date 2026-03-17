from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    session_status = request.app.state.session_store.get_status()
    current_db_label = session_status.db_label or "No database loaded"

    return request.app.state.templates.TemplateResponse(
        request,
        "index.html",
        {
            "page_title": "SQLite Browser",
            "current_db_label": current_db_label,
            "db_loaded": session_status.db_loaded,
        },
    )
