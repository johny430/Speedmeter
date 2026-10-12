import logging
import threading
from collections.abc import Iterator
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

import pytest

from enums import ExitCode
from main import main
from utils import to_megabytes


@pytest.fixture
def server_url(tmp_path: Path) -> Iterator[str]:
    """Базовый URL локального HTTP-сервера, раздающего файлы из tmp_path."""
    handler = partial(SimpleHTTPRequestHandler, directory=tmp_path)
    with HTTPServer(("127.0.0.1", 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever, args=(0.01,), daemon=True)
        thread.start()
        yield f"http://127.0.0.1:{server.server_port}"
        server.shutdown()
        thread.join()


@pytest.fixture
def image_url(server_url: str, tmp_path: Path, payload: bytes) -> str:
    image = tmp_path / "image.jpg"
    image.write_bytes(payload)
    return f"{server_url}/{image.name}"


@pytest.fixture
def missing_image_url(server_url: str) -> str:
    return f"{server_url}/missing.jpg"


def test_main_logs_summary(
    image_url: str, payload: bytes, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)
    requests = 3

    exit_code = main([image_url, "--requests", str(requests)])

    assert exit_code == ExitCode.OK
    assert f"Requests:      {requests}" in caplog.messages
    assert f"Downloaded:    {to_megabytes(requests * len(payload)):.2f} MB" in caplog.messages


def test_main_logs_failed_request(missing_image_url: str, caplog: pytest.LogCaptureFixture) -> None:
    exit_code = main([missing_image_url])

    assert exit_code == ExitCode.FAILURE
    assert caplog.records[-1].levelno == logging.ERROR
    assert caplog.records[-1].getMessage() == "request #1 failed: HTTP 404 File not found"
