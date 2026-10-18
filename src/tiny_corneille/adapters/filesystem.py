"""Filesystem access: atomic writes and the manifest bundled with the package."""

import os
import tempfile
from importlib import resources
from pathlib import Path

_FILE_MODE = 0o644


def write_bytes_atomic(path: Path, data: bytes) -> None:
    """Write the file through a temporary sibling, so readers never see a partial file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
        os.chmod(temporary, _FILE_MODE)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def read_text(path: Path) -> str:
    """Read a UTF-8 text file without translating its line endings."""
    return path.read_bytes().decode("utf-8")  # pragma: no mutate


def read_packaged_manifest() -> str:
    """Return the manifest file shipped inside the package."""
    manifest = resources.files("tiny_corneille") / "corpus_manifest.json"  # pragma: no mutate
    return manifest.read_text(encoding="utf-8")  # pragma: no mutate
