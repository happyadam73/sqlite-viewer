from __future__ import annotations

import argparse
import threading
import webbrowser
from collections.abc import Sequence
from pathlib import Path

import uvicorn

from sqlite_browser.app import create_app
from sqlite_browser.config import AppConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sqlite-browser",
        description="Run the local SQLite browser app.",
    )
    parser.add_argument(
        "--db",
        help="Path to a .sqlite, .sqlite3, or .db file to open on startup.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface to bind to. Defaults to loopback only.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the local web server to.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Start the server without opening the browser automatically.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    config = AppConfig(
        host=args.host,
        port=args.port,
        open_browser=not args.no_browser,
        db_path=Path(args.db).expanduser() if args.db else None,
        db_label=args.db,
    )
    app = create_app(config=config)

    if config.open_browser:
        url = f"http://{config.host}:{config.port}/"
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    uvicorn.run(app, host=config.host, port=config.port)
