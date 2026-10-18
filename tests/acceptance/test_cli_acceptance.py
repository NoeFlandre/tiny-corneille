import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.acceptance

GOLDEN = Path(__file__).parent.parent / "fixtures" / "expected" / "tiny_corneille.txt"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "tiny_corneille", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_build_reproduces_the_golden_corpus(raw_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "tiny_corneille.txt"

    result = _run("build", "--input-dir", str(raw_dir), "--output", str(out))

    assert result.returncode == 0, result.stderr
    assert out.read_bytes() == GOLDEN.read_bytes()


def test_cli_version_prints_the_package_version() -> None:
    result = _run("--version")

    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_cli_verify_passes_on_the_golden_corpus(manifest_file: Path) -> None:
    result = _run("verify", "--corpus", str(GOLDEN), "--manifest", str(manifest_file))

    assert result.returncode == 0, result.stderr
