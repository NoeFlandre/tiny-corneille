import json
import shutil
from pathlib import Path

import pytest

from tiny_corneille.adapters import network
from tiny_corneille.cli import EXIT_CHECK_FAILED, EXIT_ENVIRONMENT, EXIT_OK, main
from tiny_corneille.domain.manifest import sha256_hex
from tiny_corneille.domain.stats import describe


def _fake_download(raw_dir: Path):
    def download(url: str, *, timeout: float = 30.0) -> bytes:
        number = int(url.rsplit("_", 1)[1])
        return (raw_dir / f"tome_{number:02d}.txt").read_bytes()

    return download


def _stage_raw(raw_dir: Path, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for file in raw_dir.glob("tome_*.txt"):
        shutil.copy(file, directory / file.name)


def test_running_without_a_command_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as info:
        main([])

    assert info.value.code == 2


def test_top_level_help_names_the_tool_commands_and_exit_codes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as info:
        main(["--help"])

    text = " ".join(capsys.readouterr().out.split())
    assert info.value.code == 0
    assert text.startswith("usage: tiny-corneille")
    assert "COMMAND" in text
    assert "Build a clean French text corpus from the Gutenberg tomes of Corneille's works." in text
    assert "exit codes: 0 ok, 1 check failed, 2 usage error, 3 environment error" in text
    assert "fetch download the raw tomes and check their checksums" in text
    assert "build clean the raw tomes into one corpus file" in text
    assert "verify check a corpus file against the manifest" in text


@pytest.mark.parametrize(
    ("command", "phrases"),
    [
        ("fetch", ["manifest file (default: packaged)", "where to write the raw tomes"]),
        ("build", ["directory of raw tomes", "corpus file to write"]),
        ("verify", ["corpus file to check", "manifest file (default: packaged)"]),
    ],
)
def test_subcommand_help_describes_each_option(
    capsys: pytest.CaptureFixture[str], command: str, phrases: list[str]
) -> None:
    with pytest.raises(SystemExit):
        main([command, "--help"])

    text = " ".join(capsys.readouterr().out.split())
    for phrase in phrases:
        assert phrase in text


def test_build_uses_default_input_and_output_paths(
    raw_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _stage_raw(raw_dir, tmp_path / "data" / "raw")

    assert main(["build"]) == EXIT_OK
    assert (tmp_path / "data" / "tiny_corneille.txt").is_file()


def test_fetch_uses_the_default_raw_directory(
    raw_dir: Path, manifest_file: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(network, "download", _fake_download(raw_dir))

    assert main(["fetch", "--manifest", str(manifest_file)]) == EXIT_OK
    assert (tmp_path / "data" / "raw" / "tome_01.txt").is_file()


def test_verify_uses_the_default_corpus_path(
    raw_dir: Path, manifest_file: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _stage_raw(raw_dir, tmp_path / "data" / "raw")
    assert main(["build"]) == EXIT_OK

    assert main(["verify", "--manifest", str(manifest_file)]) == EXIT_OK


def test_fetch_prints_the_destination_on_success(
    raw_dir: Path,
    manifest_file: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(network, "download", _fake_download(raw_dir))
    out = tmp_path / "raw"

    main(["fetch", "--manifest", str(manifest_file), "--output-dir", str(out)])

    assert capsys.readouterr().out == f"fetched 7 tomes into {out}\n"


def test_build_prints_a_summary_with_a_stable_key_order(
    raw_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "corpus.txt"
    main(["build", "--input-dir", str(raw_dir), "--output", str(out)])

    corpus = out.read_text(encoding="utf-8")
    stats = describe(corpus)
    expected = {
        "sha256": sha256_hex(out.read_bytes()),
        "characters": stats.characters,
        "lines": stats.lines,
        "vocabulary_size": stats.vocabulary_size,
    }
    assert capsys.readouterr().out == json.dumps(expected, sort_keys=True) + "\n"


def test_verify_prints_the_checked_path_on_success(
    raw_dir: Path, manifest_file: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    corpus = tmp_path / "corpus.txt"
    main(["build", "--input-dir", str(raw_dir), "--output", str(corpus)])
    capsys.readouterr()

    main(["verify", "--corpus", str(corpus), "--manifest", str(manifest_file)])

    assert capsys.readouterr().out == f"verified {corpus}\n"


def test_missing_tome_error_names_the_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main(["build", "--input-dir", str(tmp_path), "--output", str(tmp_path / "out.txt")])

    assert capsys.readouterr().err == f"error: missing raw tome: {tmp_path / 'tome_01.txt'}\n"


def test_checksum_failures_are_listed_one_per_line(
    raw_dir: Path,
    manifest_file: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(network, "download", _fake_download(raw_dir))
    document = json.loads(manifest_file.read_text(encoding="utf-8"))
    document["sources"][0]["sha256"] = "0" * 64
    document["sources"][2]["sha256"] = "0" * 64
    manifest_file.write_text(json.dumps(document), encoding="utf-8")
    actual_1 = sha256_hex((raw_dir / "tome_01.txt").read_bytes())
    actual_3 = sha256_hex((raw_dir / "tome_03.txt").read_bytes())

    code = main(["fetch", "--manifest", str(manifest_file), "--output-dir", str(tmp_path / "raw")])

    assert code == EXIT_CHECK_FAILED
    assert capsys.readouterr().err == (
        f"error: tome 1: sha256 expected {'0' * 64}, got {actual_1}\n"
        f"tome 3: sha256 expected {'0' * 64}, got {actual_3}\n"
        "no file was written\n"
    )


def test_verify_failure_lists_each_problem_on_its_own_line(
    raw_dir: Path, manifest_file: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    corpus = tmp_path / "corpus.txt"
    main(["build", "--input-dir", str(raw_dir), "--output", str(corpus)])
    corpus.write_text("tiny", encoding="utf-8")
    capsys.readouterr()

    code = main(["verify", "--corpus", str(corpus), "--manifest", str(manifest_file)])

    lines = capsys.readouterr().err.splitlines()
    assert code == EXIT_CHECK_FAILED
    assert lines[0] == "error: verification failed:"
    assert lines[1].startswith("sha256: expected ")
    assert lines[2].startswith("characters: expected ")
    assert "XX" not in "\n".join(lines)


def test_verify_missing_corpus_error_names_the_path(
    manifest_file: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    absent = tmp_path / "absent.txt"

    code = main(["verify", "--corpus", str(absent), "--manifest", str(manifest_file)])

    assert code == EXIT_ENVIRONMENT
    assert capsys.readouterr().err == f"error: corpus not found: {absent}\n"


def test_network_failure_message_is_printed_exactly(
    manifest_file: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def offline(url: str, *, timeout: float = 30.0) -> bytes:
        raise network.DownloadError("offline")

    monkeypatch.setattr(network, "download", offline)

    code = main(["fetch", "--manifest", str(manifest_file), "--output-dir", str(tmp_path / "raw")])

    assert code == EXIT_ENVIRONMENT
    assert capsys.readouterr().err == "error: download failed: offline\n"


def test_unreadable_output_path_reports_the_os_error(
    raw_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")

    code = main(["build", "--input-dir", str(raw_dir), "--output", str(blocker / "out.txt")])

    assert code == EXIT_ENVIRONMENT
    assert capsys.readouterr().err.startswith("error: ")
