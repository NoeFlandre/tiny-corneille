import pytest

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


def _manifest(corpus_text: str) -> Manifest:
    return Manifest(
        name="tiny-corneille",
        sources=(Source(tome=1, title="Tome 01", url="https://example.test/1", sha256=ABC_SHA),),
        corpus=CorpusRecord(
            file="tiny_corneille.txt",
            sha256=sha256_hex(corpus_text.encode("utf-8")),
            characters=len(corpus_text),
            lines=len(corpus_text.splitlines()),
            vocabulary_size=len(set(corpus_text)),
        ),
    )


def test_sha256_hex_matches_known_digest() -> None:
    assert sha256_hex(b"abc") == ABC_SHA


def test_check_corpus_is_empty_when_everything_matches() -> None:
    assert check_corpus(_manifest("ab\n"), "ab\n") == ()


def test_check_corpus_reports_each_mismatch() -> None:
    problems = check_corpus(_manifest("ab\n"), "abc\n\n")

    assert any("sha256" in p for p in problems)
    assert any("characters" in p for p in problems)
    assert any("lines" in p for p in problems)
    assert any("vocabulary_size" in p for p in problems)


def test_source_problem_detects_wrong_bytes() -> None:
    source = Source(tome=1, title="Tome 01", url="https://example.test/1", sha256=ABC_SHA)

    assert source_problem(source, b"abc") is None
    assert "sha256" in (source_problem(source, b"abd") or "")


def test_parse_manifest_round_trips_a_valid_document() -> None:
    document = {
        "name": "tiny-corneille",
        "sources": [
            {"tome": 1, "title": "Tome 01", "url": "https://example.test/1", "sha256": ABC_SHA}
        ],
        "corpus": {
            "file": "tiny_corneille.txt",
            "sha256": ABC_SHA,
            "characters": 3,
            "lines": 1,
            "vocabulary_size": 3,
        },
    }

    manifest = parse_manifest(document)

    assert manifest.sources[0].tome == 1
    assert manifest.corpus.characters == 3


def test_parse_manifest_rejects_missing_keys() -> None:
    with pytest.raises(ManifestError, match="corpus"):
        parse_manifest({"name": "tiny-corneille", "sources": []})
