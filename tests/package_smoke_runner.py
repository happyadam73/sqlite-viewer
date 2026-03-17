from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_ROOT / "dist" / "sqlite-browser"
EXECUTABLE_NAME = "sqlite-browser.exe" if os.name == "nt" else "sqlite-browser"
EXECUTABLE_PATH = DIST_DIR / EXECUTABLE_NAME
DEMO_DB_PATH = REPO_ROOT / "demo" / "test.sqlite"
HOST = "127.0.0.1"
PORT = 8765
BASE_URL = f"http://{HOST}:{PORT}"
EXPECTED_BROWSER_URL = f"{BASE_URL}/"


def write_browser_capture_script(script_path: Path, output_path: Path) -> None:
    if os.name == "nt":
        script_path.write_text(
            "@echo off\n"
            f"echo %1>{output_path}\n",
            encoding="utf-8",
        )
    else:
        script_path.write_text(
            "#!/bin/sh\n"
            f"printf '%s' \"$1\" > \"{output_path}\"\n",
            encoding="utf-8",
        )
        script_path.chmod(0o755)


def read_text_if_exists(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None


def wait_for_http_ready(url: str, timeout_seconds: float = 30.0) -> str:
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=1.0) as response:
                return response.read().decode("utf-8")
        except URLError:
            time.sleep(0.25)

    raise TimeoutError(f"Timed out waiting for {url}")


def wait_for_browser_capture(output_path: Path, timeout_seconds: float = 10.0) -> str:
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        content = read_text_if_exists(output_path)
        if content:
            return content
        time.sleep(0.1)

    raise TimeoutError("Timed out waiting for the packaged app to open the browser URL.")


def main() -> int:
    if not EXECUTABLE_PATH.exists():
        raise FileNotFoundError(
            f"Packaged executable not found at {EXECUTABLE_PATH}. Run `make package` first."
        )

    if not DEMO_DB_PATH.exists():
        raise FileNotFoundError(f"Demo DB not found at {DEMO_DB_PATH}.")

    with tempfile.TemporaryDirectory(prefix="sqlite-browser-smoke-") as temp_dir:
        temp_path = Path(temp_dir)
        browser_output_path = temp_path / "browser-url.txt"
        browser_script_name = "capture-browser.cmd" if os.name == "nt" else "capture-browser.sh"
        browser_script_path = temp_path / browser_script_name
        write_browser_capture_script(browser_script_path, browser_output_path)

        browser_command = f'"{browser_script_path}" %s' if os.name == "nt" else f'{browser_script_path} %s'

        env = os.environ.copy()
        env["SQLITE_BROWSER_BROWSER_COMMAND"] = browser_command

        process = subprocess.Popen(
            [
                str(EXECUTABLE_PATH),
                str(DEMO_DB_PATH),
                "--host",
                HOST,
                "--port",
                str(PORT),
            ],
            cwd=REPO_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            browser_url = wait_for_browser_capture(browser_output_path)
            assert browser_url == EXPECTED_BROWSER_URL

            root_html = wait_for_http_ready(f"{BASE_URL}/")
            assert 'data-testid="app-shell"' in root_html

            status_json = wait_for_http_ready(f"{BASE_URL}/api/status")
            status = json.loads(status_json)
            assert status["db_loaded"] is True
            assert status["db_label"] == str(DEMO_DB_PATH)

            css_text = wait_for_http_ready(f"{BASE_URL}/static/app.css")
            assert ":root" in css_text

            if process.poll() is not None:
                stdout, stderr = process.communicate(timeout=1)
                raise RuntimeError(
                    f"Packaged app exited unexpectedly with code {process.returncode}.\n"
                    f"stdout:\n{stdout}\n"
                    f"stderr:\n{stderr}"
                )
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
