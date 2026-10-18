import re
from pathlib import Path

import pytest

from tiny_corneille.cli import EXIT_CHECK_FAILED, main


def _has_phrase(phrase: str, text: str) -> bool:
    """True when the phrase appears as whole words, not glued to other text."""
    return re.search(rf"(?<!\S){re.escape(phrase)}(?!\S)", text) is not None


def test_top_level_help_frames_the_description_command_and_epilog(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        main(["--help"])

    text = " ".join(capsys.readouterr().out.split())
    assert _has_phrase(
        "Build a clean French text corpus from the Gutenberg tomes of Corneille's works.", text
    )
    assert _has_phrase("COMMAND", text)
    assert text.endswith("exit codes: 0 ok, 1 check failed, 2 usage error, 3 environment error")


@pytest.mark.parametrize(
    ("command", "phrase"),
    [
        ("fetch", "manifest file (default: packaged)"),
        ("fetch", "where to write the raw tomes"),
        ("build", "directory of raw tomes"),
        ("build", "corpus file to write"),
        ("verify", "corpus file to check"),
        ("verify", "manifest file (default: packaged)"),
    ],
)
def test_each_option_help_is_framed_exactly(
    capsys: pytest.CaptureFixture[str], command: str, phrase: str
) -> None:
    with pytest.raises(SystemExit):
        main([command, "--help"])

    assert _has_phrase(phrase, " ".join(capsys.readouterr().out.split()))


def test_invalid_manifest_error_message_is_exact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")

    code = main(["fetch", "--manifest", str(manifest), "--output-dir", str(tmp_path / "raw")])

    assert code == EXIT_CHECK_FAILED
    assert capsys.readouterr().err == "error: invalid manifest: bad field 'name'\n"
