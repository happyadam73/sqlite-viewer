from __future__ import annotations

import argparse
import threading
import webbrowser
from collections.abc import Sequence

import uvicorn

from sqlite_browser.app import create_app
from sqlite_browser.config import AppConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sqlite-browser",
        description="Run the local SQLite browser app.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    build_parser().parse_args(argv)

    config = AppConfig()
    app = create_app(config=config)

    if config.open_browser:
        url = f"http://{config.host}:{config.port}/"
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    uvicorn.run(app, host=config.host, port=config.port)
