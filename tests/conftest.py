import json
import urllib.request
from pathlib import Path

import pytest

from tiny_corneille.domain.corpus import build_corpus
from tiny_corneille.domain.manifest import sha256_hex
from tiny_corneille.domain.stats import describe

FIXTURES = Path(__file__).parent / "fixtures"
TOME_COUNT = 7


@pytest.fixture(autouse=True)
def _forbid_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """No test reaches the network; a test that needs downloads injects its own fake."""

    def refuse(self: object, fullurl: object, data: object = None, timeout: object = None) -> None:
        raise AssertionError(f"unexpected network access: {getattr(fullurl, 'full_url', fullurl)}")

    monkeypatch.setattr(urllib.request.OpenerDirector, "open", refuse)


@pytest.fixture
def raw_dir() -> Path:
    """Directory of the seven raw tome fixtures, named tome_01.txt to tome_07.txt."""
    return FIXTURES / "raw"


@pytest.fixture
def manifest_file(tmp_path: Path, raw_dir: Path) -> Path:
    """Write a manifest whose checksums and statistics match the fixtures exactly."""
    raws = [(raw_dir / f"tome_{n:02d}.txt").read_bytes() for n in range(1, TOME_COUNT + 1)]
    corpus = build_corpus([raw.decode("utf-8") for raw in raws])
    stats = describe(corpus)
    document = {
        "name": "tiny-corneille",
        "sources": [
            {
                "tome": n,
                "title": f"Tome {n:02d}",
                "url": f"https://example.test/tome_{n:02d}",
                "sha256": sha256_hex(raw),
            }
            for n, raw in enumerate(raws, start=1)
        ],
        "corpus": {
            "file": "tiny_corneille.txt",
            "sha256": sha256_hex(corpus.encode("utf-8")),
            "characters": stats.characters,
            "lines": stats.lines,
            "vocabulary_size": stats.vocabulary_size,
        },
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
