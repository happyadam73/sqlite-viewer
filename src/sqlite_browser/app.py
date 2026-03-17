from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlite_browser.config import AppConfig
from sqlite_browser.routes.api import router as api_router
from sqlite_browser.routes.pages import router as pages_router
from sqlite_browser.session_store import SessionStore


def create_app(
    *,
    config: AppConfig | None = None,
    session_store: SessionStore | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application."""

    app_config = config or AppConfig()
    store = session_store or SessionStore()
    package_dir = Path(__file__).resolve().parent
    templates = Jinja2Templates(directory=str(package_dir / "templates"))

    app = FastAPI(title="SQLite Browser")
    app.state.config = app_config
    app.state.session_store = store
    app.state.templates = templates

    app.mount("/static", StaticFiles(directory=package_dir / "static"), name="static")
    app.include_router(pages_router)
    app.include_router(api_router)

    return app
