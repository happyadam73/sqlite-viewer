from __future__ import annotations

from pathlib import Path

import pytest

from sqlite_browser import cli


def test_parse_args_supports_positional_db_path() -> None:
    args = cli.parse_args(["demo/test.sqlite"])

    assert args.db_path == "demo/test.sqlite"
    assert args.db_option is None
    assert args.db == "demo/test.sqlite"


@pytest.mark.parametrize("db_flag", ["--db", "-d"])
def test_parse_args_supports_flag_based_db_path(db_flag: str) -> None:
    args = cli.parse_args(
        [db_flag, "demo/test.sqlite", "--host", "127.0.0.2", "--port", "8765", "--no-browser"]
    )

    assert args.db_path is None
    assert args.db_option == "demo/test.sqlite"
    assert args.db == "demo/test.sqlite"
    assert args.host == "127.0.0.2"
    assert args.port == 8765
    assert args.no_browser is True


def test_parse_args_rejects_ambiguous_db_inputs() -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.parse_args(["demo/test.sqlite", "--db", "other.sqlite"])

    assert exc_info.value.code == 2


@pytest.mark.parametrize(
    ("host", "expected_url"),
    [
        ("127.0.0.1", "http://127.0.0.1:8000/"),
        ("localhost", "http://localhost:8000/"),
        ("0.0.0.0", "http://127.0.0.1:8000/"),
        ("::", "http://127.0.0.1:8000/"),
        ("::1", "http://[::1]:8000/"),
    ],
)
def test_build_browser_url_handles_loopback_and_ipv6(host: str, expected_url: str) -> None:
    assert cli.build_browser_url(host, 8000) == expected_url


def test_open_browser_url_uses_custom_browser_command(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeBrowser:
        def open(self, url: str) -> None:
            captured["opened_url"] = url

    def fake_get(command: str) -> FakeBrowser:
        captured["command"] = command
        return FakeBrowser()

    monkeypatch.setenv(cli.BROWSER_COMMAND_ENV, "/tmp/browser %s")
    monkeypatch.setattr(cli.webbrowser, "get", fake_get)

    cli.open_browser_url("http://127.0.0.1:8000/")

    assert captured["command"] == "/tmp/browser %s"
    assert captured["opened_url"] == "http://127.0.0.1:8000/"


def test_main_starts_without_db_and_schedules_browser_open(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_create_app(*, config):
        captured["config"] = config
        return "app"

    def fake_run(app, *, host, port):
        captured["run"] = {"app": app, "host": host, "port": port}

    class FakeTimer:
        def __init__(self, interval, callback):
            captured["timer"] = {"interval": interval, "callback": callback}

        def start(self) -> None:
            captured["timer_started"] = True

    monkeypatch.setattr(cli, "create_app", fake_create_app)
    monkeypatch.setattr(cli.uvicorn, "run", fake_run)
    monkeypatch.setattr(cli.threading, "Timer", FakeTimer)
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: captured.setdefault("opened_url", url))

    cli.main([])

    config = captured["config"]
    assert config.host == "127.0.0.1"
    assert config.port == 8000
    assert config.open_browser is True
    assert config.db_path is None
    assert config.db_label is None
    assert captured["timer_started"] is True
    assert captured["run"] == {"app": "app", "host": "127.0.0.1", "port": 8000}


def test_main_passes_flag_config_to_app_without_opening_browser(monkeypatch, sample_db: Path) -> None:
    captured: dict[str, object] = {}

    def fake_create_app(*, config):
        captured["config"] = config
        return "app"

    def fake_run(app, *, host, port):
        captured["run"] = {"app": app, "host": host, "port": port}

    class FakeTimer:
        def __init__(self, interval, callback):
            captured["timer"] = {"interval": interval, "callback": callback}

        def start(self) -> None:
            captured["timer_started"] = True

    monkeypatch.setattr(cli, "create_app", fake_create_app)
    monkeypatch.setattr(cli.uvicorn, "run", fake_run)
    monkeypatch.setattr(cli.threading, "Timer", FakeTimer)

    cli.main(["-d", str(sample_db), "--host", "127.0.0.1", "--port", "8765", "--no-browser"])

    config = captured["config"]
    assert config.host == "127.0.0.1"
    assert config.port == 8765
    assert config.open_browser is False
    assert config.db_path == sample_db
    assert config.db_label == str(sample_db)
    assert "timer" not in captured
    assert captured["run"] == {"app": "app", "host": "127.0.0.1", "port": 8765}


def test_main_opens_loopback_browser_url_for_wildcard_host(monkeypatch, sample_db: Path) -> None:
    captured: dict[str, object] = {}

    def fake_create_app(*, config):
        captured["config"] = config
        return "app"

    def fake_run(app, *, host, port):
        captured["run"] = {"app": app, "host": host, "port": port}

    class FakeTimer:
        def __init__(self, interval, callback):
            captured["timer"] = {"interval": interval, "callback": callback}

        def start(self) -> None:
            captured["timer_started"] = True

    monkeypatch.setattr(cli, "create_app", fake_create_app)
    monkeypatch.setattr(cli.uvicorn, "run", fake_run)
    monkeypatch.setattr(cli.threading, "Timer", FakeTimer)
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: captured.setdefault("opened_url", url))

    cli.main([str(sample_db), "--host", "0.0.0.0", "--port", "8765"])

    config = captured["config"]
    assert config.db_path == sample_db
    assert config.db_label == str(sample_db)
    assert config.open_browser is True
    assert captured["timer_started"] is True

    timer = captured["timer"]
    assert timer["interval"] == 0.8
    timer["callback"]()
    assert captured["opened_url"] == "http://127.0.0.1:8765/"
    assert captured["run"] == {"app": "app", "host": "0.0.0.0", "port": 8765}
