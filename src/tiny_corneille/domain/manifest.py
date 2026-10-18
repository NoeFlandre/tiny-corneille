"""Manifest that pins the source checksums and the expected corpus statistics."""

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from tiny_corneille.domain.stats import describe


class ManifestError(ValueError):
    """The manifest document is missing a field or has a wrong type."""


@dataclass(frozen=True)
class Source:
    """One Gutenberg tome: its URL and the SHA-256 of the raw download."""

    tome: int
    title: str
    url: str
    sha256: str


@dataclass(frozen=True)
class CorpusRecord:
    """The expected corpus file: checksum and statistics."""

    file: str
    sha256: str
    characters: int
    lines: int
    vocabulary_size: int


@dataclass(frozen=True)
class Manifest:
    """All sources and the expected corpus."""

    name: str
    sources: tuple[Source, ...]
    corpus: CorpusRecord


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_problem(source: Source, raw: bytes) -> str | None:
    """Return a problem description when the raw bytes do not match the pinned checksum."""
    actual = sha256_hex(raw)
    if actual == source.sha256:
        return None
    return f"tome {source.tome}: sha256 expected {source.sha256}, got {actual}"


def check_corpus(manifest: Manifest, text: str) -> tuple[str, ...]:
    """Return one problem per field where the corpus differs from the manifest."""
    record = manifest.corpus
    stats = describe(text)
    actual_sha = sha256_hex(text.encode("utf-8"))  # pragma: no mutate
    expected_and_actual = {
        "sha256": (record.sha256, actual_sha),
        "characters": (record.characters, stats.characters),
        "lines": (record.lines, stats.lines),
        "vocabulary_size": (record.vocabulary_size, stats.vocabulary_size),
    }
    return tuple(
        f"{field}: expected {expected}, got {actual}"
        for field, (expected, actual) in expected_and_actual.items()
        if expected != actual
    )


def parse_manifest(document: Mapping[str, Any]) -> Manifest:
    """Build a Manifest from a decoded JSON document."""
    try:
        return Manifest(
            name=str(document["name"]),
            sources=tuple(_parse_source(item) for item in document["sources"]),
            corpus=_parse_corpus(document["corpus"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ManifestError(f"bad field {error}") from error


def _parse_source(item: Mapping[str, Any]) -> Source:
    return Source(
        tome=int(item["tome"]),
        title=str(item["title"]),
        url=str(item["url"]),
        sha256=str(item["sha256"]),
    )


def _parse_corpus(item: Mapping[str, Any]) -> CorpusRecord:
    return CorpusRecord(
        file=str(item["file"]),
        sha256=str(item["sha256"]),
        characters=int(item["characters"]),
        lines=int(item["lines"]),
        vocabulary_size=int(item["vocabulary_size"]),
    )
