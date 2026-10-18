import json
from pathlib import Path

import pytest

from tiny_corneille.adapters import network
from tiny_corneille.cli import EXIT_CHECK_FAILED, EXIT_ENVIRONMENT, EXIT_OK, main

TOMES = 7


def _fake_download(raw_dir: Path):
    def download(url: str, *, timeout: float = 30.0) -> bytes:
        number = int(url.rsplit("_", 1)[1])
        return (raw_dir / f"tome_{number:02d}.txt").read_bytes()

    return download


def test_fetch_writes_every_tome_when_checksums_match(
    monkeypatch: pytest.MonkeyPatch, raw_dir: Path, manifest_file: Path, tmp_path: Path
) -> None:
    monkeypatch.setattr(network, "download", _fake_download(raw_dir))
    out = tmp_path / "raw"

    code = main(["fetch", "--manifest", str(manifest_file), "--output-dir", str(out)])

    assert code == EXIT_OK
    for n in range(1, TOMES + 1):
        assert (out / f"tome_{n:02d}.txt").read_bytes() == (
            raw_dir / f"tome_{n:02d}.txt"
        ).read_bytes()


def test_fetch_refuses_a_bad_checksum_and_writes_nothing(
    monkeypatch: pytest.MonkeyPatch,
    raw_dir: Path,
    manifest_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(network, "download", _fake_download(raw_dir))
    document = json.loads(manifest_file.read_text(encoding="utf-8"))
    document["sources"][2]["sha256"] = "0" * 64
    manifest_file.write_text(json.dumps(document), encoding="utf-8")
    out = tmp_path / "raw"

    code = main(["fetch", "--manifest", str(manifest_file), "--output-dir", str(out)])

    assert code == EXIT_CHECK_FAILED
    assert "tome 3" in capsys.readouterr().err
    assert not out.exists() or not any(out.iterdir())


def test_fetch_network_failure_exits_with_environment_code(
    monkeypatch: pytest.MonkeyPatch, manifest_file: Path, tmp_path: Path
) -> None:
    def offline(url: str, *, timeout: float = 30.0) -> bytes:
        raise network.DownloadError("offline")

    monkeypatch.setattr(network, "download", offline)

    code = main(["fetch", "--manifest", str(manifest_file), "--output-dir", str(tmp_path / "raw")])

    assert code == EXIT_ENVIRONMENT


def test_build_writes_corpus_and_prints_a_json_summary(
    raw_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "tiny_corneille.txt"

    code = main(["build", "--input-dir", str(raw_dir), "--output", str(out)])

    summary = json.loads(capsys.readouterr().out)
    assert code == EXIT_OK
    assert summary["characters"] == len(out.read_text(encoding="utf-8"))
    assert set(summary) >= {"sha256", "characters", "lines", "vocabulary_size"}


def test_build_with_a_missing_tome_exits_with_environment_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(["build", "--input-dir", str(tmp_path), "--output", str(tmp_path / "out.txt")])

    assert code == EXIT_ENVIRONMENT
    assert "tome_01.txt" in capsys.readouterr().err


def test_verify_accepts_a_matching_corpus(
    raw_dir: Path, manifest_file: Path, tmp_path: Path
) -> None:
    corpus = tmp_path / "tiny_corneille.txt"
    main(["build", "--input-dir", str(raw_dir), "--output", str(corpus)])

    assert main(["verify", "--corpus", str(corpus), "--manifest", str(manifest_file)]) == EXIT_OK


def test_verify_rejects_an_edited_corpus(
    raw_dir: Path, manifest_file: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    corpus = tmp_path / "tiny_corneille.txt"
    main(["build", "--input-dir", str(raw_dir), "--output", str(corpus)])
    corpus.write_text(corpus.read_text(encoding="utf-8") + "x", encoding="utf-8")

    code = main(["verify", "--corpus", str(corpus), "--manifest", str(manifest_file)])

    assert code == EXIT_CHECK_FAILED
    assert "sha256" in capsys.readouterr().err


def test_unknown_command_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as info:
        main(["nonsense"])

    assert info.value.code == 2


def test_fetch_with_an_invalid_manifest_exits_with_check_failure(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")

    code = main(["fetch", "--manifest", str(manifest), "--output-dir", str(tmp_path / "raw")])

    assert code == EXIT_CHECK_FAILED


def test_verify_with_a_missing_corpus_exits_with_environment_code(
    manifest_file: Path, tmp_path: Path
) -> None:
    code = main(
        ["verify", "--corpus", str(tmp_path / "absent.txt"), "--manifest", str(manifest_file)]
    )

    assert code == EXIT_ENVIRONMENT


def test_build_below_a_regular_file_exits_with_environment_code(
    raw_dir: Path, tmp_path: Path
) -> None:
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")

    code = main(["build", "--input-dir", str(raw_dir), "--output", str(blocker / "out.txt")])

    assert code == EXIT_ENVIRONMENT
