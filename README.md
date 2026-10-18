# Tiny Corneille

A clean French text corpus from the seven Project Gutenberg tomes of Pierre Corneille's works. It follows the idea of Andrej Karpathy's tiny Shakespeare.

- **Data:** [huggingface.co/datasets/NoeFlandre/tiny-corneille](https://huggingface.co/datasets/NoeFlandre/tiny-corneille)
- **Documentation:** build it with `uv run mkdocs serve` (see [docs/](docs/index.md))

## Quick start

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12 or later.

```bash
uv sync --locked
uv run tiny-corneille fetch
uv run tiny-corneille build
uv run tiny-corneille verify
```

The corpus is written to `data/tiny_corneille.txt`. Run `uv run tiny-corneille --help` for all commands and exit codes.

## Docker

```bash
docker build -t tiny-corneille .
docker run --rm -v "$PWD/data:/work/data" tiny-corneille build
```

## Development

Run the gates in [docs/quality.md](docs/quality.md) in order. The main commands are:

```bash
uv run ruff format --check . && uv run ruff check . && uv run ty check
uv run pytest --cov && uv run lint-imports
uv run mutmut run && uv run mutmut results
```

## Licence and sources

The texts are public domain. They come from Project Gutenberg, which keeps its own terms. The cleaned corpus and its checksums are on the Hugging Face dataset page above.
