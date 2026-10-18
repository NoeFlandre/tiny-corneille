import os
import urllib.request
from pathlib import Path
from typing import Any

import pytest

from tiny_corneille.adapters import filesystem, network


class _Body:
    def __enter__(self) -> "_Body":
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None

    def read(self) -> bytes:
        return b""


def test_write_bytes_atomic_creates_several_missing_directories(tmp_path: Path) -> None:
    target = tmp_path / "a" / "b" / "out.txt"

    filesystem.write_bytes_atomic(target, b"x")

    assert target.read_bytes() == b"x"


def test_write_bytes_atomic_stages_the_temporary_file_next_to_the_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[dict[str, Any]] = []
    real_mkstemp = filesystem.tempfile.mkstemp

    def recording_mkstemp(**kwargs: Any) -> tuple[int, str]:
        calls.append(kwargs)
        return real_mkstemp(**kwargs)

    monkeypatch.setattr(filesystem.tempfile, "mkstemp", recording_mkstemp)

    filesystem.write_bytes_atomic(tmp_path / "out.txt", b"x")

    assert calls == [{"dir": tmp_path, "prefix": ".out.txt.", "suffix": ".tmp"}]


def test_failed_replace_reports_the_original_error_when_temp_file_is_gone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def replace_then_fail(source: str, destination: str) -> None:
        os.unlink(source)
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", replace_then_fail)

    with pytest.raises(OSError, match="disk full"):
        filesystem.write_bytes_atomic(tmp_path / "out.txt", b"data")

    assert list(tmp_path.iterdir()) == []


def test_written_file_has_standard_read_permissions(tmp_path: Path) -> None:
    target = tmp_path / "out.txt"

    filesystem.write_bytes_atomic(target, b"x")

    assert target.stat().st_mode & 0o777 == 0o644


def test_download_defaults_to_a_thirty_second_timeout() -> None:
    seen: dict[str, float] = {}

    def opener(request: urllib.request.Request, timeout: float) -> _Body:
        seen["timeout"] = timeout
        return _Body()

    network.download("https://example.test/t", open_url=opener)

    assert seen["timeout"] == 30.0
