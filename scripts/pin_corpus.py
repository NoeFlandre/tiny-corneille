"""Release step: write the corpus checksum and statistics into the packaged manifest.

Usage, from the project root, after `tiny-corneille build`:
    uv run python scripts/pin_corpus.py data/tiny_corneille.txt
"""

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from tiny_corneille.domain.manifest import sha256_hex
from tiny_corneille.domain.stats import describe

MANIFEST = Path("src/tiny_corneille/corpus_manifest.json")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pin the corpus record in the packaged manifest.")
    parser.add_argument("corpus", type=Path, help="corpus file built by tiny-corneille build")
    args = parser.parse_args(argv)

    data = args.corpus.read_bytes()
    stats = describe(data.decode("utf-8"))
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    document["corpus"] = {
        "file": "tiny_corneille.txt",
        "sha256": sha256_hex(data),
        "characters": stats.characters,
        "lines": stats.lines,
        "vocabulary_size": stats.vocabulary_size,
    }
    MANIFEST.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"pinned {args.corpus} into {MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
