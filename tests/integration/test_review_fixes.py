import http.client
import shutil
import urllib.request
from pathlib import Path

import pytest

from tiny_corneille.adapters import filesystem, network
from tiny_corneille.cli import EXIT_CHECK_FAILED, EXIT_ENVIRONMENT, main


class _Body:
    def __init__(self, payload: bytes = b"", error: BaseException | None = None) -> None:
        self._payload = payload
        self._error = error

    def __enter__(self) -> "_Body":
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None

    def read(self) -> bytes:
        if self._error is not None:
            raise self._error
        return self._payload


def test_truncated_body_is_a_download_error() -> None:
    def opener(request: urllib.request.Request, timeout: float) -> _Body:
        return _Body(error=http.client.IncompleteRead(b"ten bytes!", 990))

    with pytest.raises(network.DownloadError, match=r"IncompleteRead|bytes read"):
        network.download("https://example.test/t", open_url=opener)


def test_redirect_to_plain_http_is_refused() -> None:
    handler = network.HttpsOnlyRedirectHandler()
    request = urllib.request.Request("https://example.test/t")

    with pytest.raises(network.DownloadError, match="non-HTTPS"):
        handler.redirect_request(request, None, 302, "Found", {}, "http://example.test/elsewhere")


def test_redirect_to_https_is_followed() -> None:
    handler = network.HttpsOnlyRedirectHandler()
    request = urllib.request.Request("https://example.test/t")

    redirected = handler.redirect_request(
        request, None, 302, "Found", {}, "https://example.test/elsewhere"
    )

    assert redirected is not None
    assert redirected.full_url == "https://example.test/elsewhere"


def test_read_text_keeps_crlf_so_checksums_see_the_real_bytes(tmp_path: Path) -> None:
    path = tmp_path / "corpus.txt"
    path.write_bytes(b"a\r\nb\r\n")

    assert filesystem.read_text(path) == "a\r\nb\r\n"


def test_verify_rejects_a_corpus_whose_line_endings_were_converted(
    raw_dir: Path, manifest_file: Path, tmp_path: Path
) -> None:
    corpus = tmp_path / "corpus.txt"
    main(["build", "--input-dir", str(raw_dir), "--output", str(corpus)])
    corpus.write_bytes(corpus.read_bytes().replace(b"\n", b"\r\n"))

    code = main(["verify", "--corpus", str(corpus), "--manifest", str(manifest_file)])

    assert code == EXIT_CHECK_FAILED


def test_verify_reports_a_file_that_is_not_utf8(
    raw_dir: Path, manifest_file: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    corpus = tmp_path / "corpus.txt"
    corpus.write_bytes(b"Caf\xe9 de Corneille\n")

    code = main(["verify", "--corpus", str(corpus), "--manifest", str(manifest_file)])

    assert code == EXIT_CHECK_FAILED
    assert capsys.readouterr().err.startswith("error: invalid input: ")


def test_build_reports_a_tome_without_gutenberg_markers(
    raw_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    input_dir = tmp_path / "raw"
    shutil.copytree(raw_dir, input_dir)
    (input_dir / "tome_04.txt").write_text("no markers here\n", encoding="utf-8")

    code = main(["build", "--input-dir", str(input_dir), "--output", str(tmp_path / "out.txt")])

    assert code == EXIT_CHECK_FAILED
    assert capsys.readouterr().err == "error: invalid input: START marker not found\n"


def test_failed_write_mid_fetch_reports_how_many_tomes_were_written(
    raw_dir: Path,
    manifest_file: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def download(url: str, *, timeout: float = 30.0) -> bytes:
        number = int(url.rsplit("_", 1)[1])
        return (raw_dir / f"tome_{number:02d}.txt").read_bytes()

    monkeypatch.setattr(network, "download", download)
    real_write = filesystem.write_bytes_atomic
    calls = {"count": 0}

    def failing_on_third(path: Path, data: bytes) -> None:
        calls["count"] += 1
        if calls["count"] == 3:
            raise OSError("disk full")
        real_write(path, data)

    monkeypatch.setattr(filesystem, "write_bytes_atomic", failing_on_third)

    code = main(["fetch", "--manifest", str(manifest_file), "--output-dir", str(tmp_path / "raw")])

    assert code == EXIT_ENVIRONMENT
    assert capsys.readouterr().err == (
        "error: write failed after 2 of 7 tomes: disk full\nthe output directory may mix versions\n"
    )
