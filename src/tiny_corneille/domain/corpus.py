"""Compose the cleaning rules into the corpus build."""

from collections.abc import Sequence

from tiny_corneille.domain.cleaning import clean
from tiny_corneille.domain.gutenberg import extract_body


def build_tome(raw: str) -> str:
    """Turn the raw Gutenberg text of one tome into clean corpus text."""
    return clean(extract_body(raw))


def build_corpus(raws: Sequence[str]) -> str:
    """Build the corpus from the raw texts, in order, one blank line between tomes."""
    return "\n".join(build_tome(raw) for raw in raws)
