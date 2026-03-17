from __future__ import annotations

import argparse
import os
import threading
import webbrowser
from collections.abc import Sequence
from pathlib import Path

import uvicorn

from sqlite_browser.app import create_app
from sqlite_browser.config import AppConfig


WILDCARD_BIND_HOSTS = {"0.0.0.0", "::", "[::]"}
BROWSER_COMMAND_ENV = "SQLITE_BROWSER_BROWSER_COMMAND"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sqlite-browser",
        description="Run the local SQLite browser app.",
    )
    parser.add_argument(
        "db_path",
        nargs="?",
        help="Path to a .sqlite, .sqlite3, or .db file to open on startup.",
    )
    parser.add_argument(
        "-d",
        "--db",
        dest="db_option",
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


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.db_path and args.db_option:
        parser.error("Provide either DB_PATH or --db/-d, but not both.")

    args.db = args.db_option or args.db_path
    return args


def build_browser_url(host: str, port: int) -> str:
    browser_host = "127.0.0.1" if host in WILDCARD_BIND_HOSTS else host
    if ":" in browser_host and not browser_host.startswith("["):
        browser_host = f"[{browser_host}]"
    return f"http://{browser_host}:{port}/"


def open_browser_url(url: str) -> None:
    browser_command = os.getenv(BROWSER_COMMAND_ENV)
    if browser_command:
        webbrowser.get(browser_command).open(url)
        return

    webbrowser.open(url)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    config = AppConfig(
        host=args.host,
        port=args.port,
        open_browser=not args.no_browser,
        db_path=Path(args.db).expanduser() if args.db else None,
        db_label=args.db,
    )
    app = create_app(config=config)

    if config.open_browser:
        url = build_browser_url(config.host, config.port)
        threading.Timer(0.8, lambda: open_browser_url(url)).start()

    uvicorn.run(app, host=config.host, port=config.port)
