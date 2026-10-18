"""Count GPT-2 tokens in a corpus file. A one-off measurement, not part of the package.

Usage, from the project root:
    uv run --with tiktoken python scripts/count_gpt2_tokens.py data/tiny_corneille.txt
"""

import sys
from pathlib import Path

import tiktoken


def main(argv: list[str]) -> int:
    text = Path(argv[1]).read_text(encoding="utf-8")
    encoding = tiktoken.get_encoding("gpt2")
    tokens = len(encoding.encode_ordinary(text))
    print(f"gpt2 tokens: {tokens}")
    print(f"characters per token: {len(text) / tokens:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
