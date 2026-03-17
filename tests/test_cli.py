from __future__ import annotations

from pathlib import Path

from sqlite_browser import cli


def test_build_parser_supports_milestone_two_options() -> None:
    args = cli.build_parser().parse_args(
        ["--db", "demo/test.sqlite", "--host", "127.0.0.2", "--port", "8765", "--no-browser"]
    )

    assert args.db == "demo/test.sqlite"
    assert args.host == "127.0.0.2"
    assert args.port == 8765
    assert args.no_browser is True


def test_main_passes_cli_config_to_app(monkeypatch, sample_db: Path) -> None:
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

    cli.main(["--db", str(sample_db), "--host", "127.0.0.1", "--port", "8765", "--no-browser"])

    config = captured["config"]
    assert config.host == "127.0.0.1"
    assert config.port == 8765
    assert config.open_browser is False
    assert config.db_path == sample_db
    assert config.db_label == str(sample_db)
    assert "timer" not in captured
    assert captured["run"] == {"app": "app", "host": "127.0.0.1", "port": 8765}
