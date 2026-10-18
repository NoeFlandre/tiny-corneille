import pytest

from tiny_corneille.domain.gutenberg import BoilerplateError, extract_body
from tiny_corneille.domain.manifest import (
    CorpusRecord,
    Manifest,
    ManifestError,
    Source,
    check_corpus,
    parse_manifest,
    sha256_hex,
    source_problem,
)

ABC_SHA = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
ZERO_SHA = "0" * 64


def test_missing_start_marker_message_is_exact() -> None:
    with pytest.raises(BoilerplateError) as info:
        extract_body("*** END OF THE PROJECT GUTENBERG EBOOK X ***\n")

    assert str(info.value) == "START marker not found"


def test_missing_end_marker_message_is_exact() -> None:
    with pytest.raises(BoilerplateError) as info:
        extract_body("*** START OF THE PROJECT GUTENBERG EBOOK X ***\nbody\n")

    assert str(info.value) == "END marker not found"


def test_check_corpus_reports_every_field_with_an_exact_message() -> None:
    manifest = Manifest(
        name="tiny-corneille",
        sources=(),
        corpus=CorpusRecord(
            file="tiny_corneille.txt", sha256=ZERO_SHA, characters=0, lines=0, vocabulary_size=0
        ),
    )

    assert check_corpus(manifest, "ab\n") == (
        f"sha256: expected {ZERO_SHA}, got {sha256_hex(b'ab\n')}",
        "characters: expected 0, got 3",
        "lines: expected 0, got 1",
        "vocabulary_size: expected 0, got 3",
    )


def test_source_problem_message_names_the_tome_and_both_digests() -> None:
    source = Source(tome=4, title="Tome 04", url="https://example.test/4", sha256=ABC_SHA)

    assert source_problem(source, b"abd") == (
        f"tome 4: sha256 expected {ABC_SHA}, got {sha256_hex(b'abd')}"
    )


def test_parse_manifest_keeps_every_field() -> None:
    document = {
        "name": "tiny-corneille",
        "sources": [
            {"tome": 2, "title": "Tome 02", "url": "https://example.test/2", "sha256": ABC_SHA}
        ],
        "corpus": {
            "file": "c.txt",
            "sha256": ZERO_SHA,
            "characters": 4,
            "lines": 2,
            "vocabulary_size": 3,
        },
    }

    assert parse_manifest(document) == Manifest(
        name="tiny-corneille",
        sources=(Source(tome=2, title="Tome 02", url="https://example.test/2", sha256=ABC_SHA),),
        corpus=CorpusRecord(
            file="c.txt", sha256=ZERO_SHA, characters=4, lines=2, vocabulary_size=3
        ),
    )


def test_parse_manifest_error_names_the_missing_field() -> None:
    with pytest.raises(ManifestError) as info:
        parse_manifest({"name": "tiny-corneille", "sources": []})

    assert str(info.value) == "bad field 'corpus'"
