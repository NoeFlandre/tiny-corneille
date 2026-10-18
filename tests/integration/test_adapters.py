import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import pytest

from tiny_corneille.adapters import filesystem, network
from tiny_corneille.domain.manifest import parse_manifest


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None

    def read(self) -> bytes:
        return self._payload


def test_download_returns_body_and_sends_identifying_user_agent() -> None:
    seen: dict[str, Any] = {}

    def opener(request: urllib.request.Request, timeout: float) -> _FakeResponse:
        seen["url"] = request.full_url
        seen["timeout"] = timeout
        seen["agent"] = request.get_header("User-agent")
        return _FakeResponse(b"raw bytes")

    body = network.download("https://example.test/t", open_url=opener, timeout=5)

    assert body == b"raw bytes"
    assert seen["url"] == "https://example.test/t"
    assert seen["timeout"] == 5
    assert "tiny-corneille" in str(seen["agent"])


def test_download_wraps_transport_errors() -> None:
    def opener(request: urllib.request.Request, timeout: float) -> _FakeResponse:
        raise urllib.error.URLError("offline")

    with pytest.raises(network.DownloadError, match="offline"):
        network.download("https://example.test/t", open_url=opener)


def test_download_refuses_non_https_urls() -> None:
    def opener(request: urllib.request.Request, timeout: float) -> _FakeResponse:
        raise AssertionError("must not open a non-HTTPS URL")

    with pytest.raises(network.DownloadError, match="non-HTTPS"):
        network.download("file:///etc/passwd", open_url=opener)


def test_write_bytes_atomic_creates_parents_and_replaces_content(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "out.txt"

    filesystem.write_bytes_atomic(target, b"first")
    filesystem.write_bytes_atomic(target, b"second")

    assert target.read_bytes() == b"second"
    assert list(target.parent.iterdir()) == [target]


def test_write_bytes_atomic_removes_its_temporary_file_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "out.txt"

    def failing_replace(source: str, destination: str) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", failing_replace)

    with pytest.raises(OSError, match="disk full"):
        filesystem.write_bytes_atomic(target, b"data")

    assert list(tmp_path.iterdir()) == []


def test_packaged_manifest_is_a_valid_manifest_document() -> None:
    manifest = parse_manifest(json.loads(filesystem.read_packaged_manifest()))

    assert manifest.name == "tiny-corneille"
