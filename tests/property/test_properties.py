import re

from hypothesis import given
from hypothesis import strategies as st

from tiny_corneille.domain import cleaning
from tiny_corneille.domain.corpus import build_tome
from tiny_corneille.domain.gutenberg import extract_body
from tiny_corneille.domain.manifest import CorpusRecord, Manifest, check_corpus, sha256_hex
from tiny_corneille.domain.stats import describe

any_text = st.text(max_size=400)
body_text = st.text(max_size=400).filter(lambda s: "*" not in s)
note_ref = re.compile(r"\[\d+(?:-[a-z])?\]")
tome_fragment = st.sampled_from(
    [
        "NOTICE.",
        "AU LECTEUR.",
        "ACTEURS.",
        "LISTE DES ÉDITIONS X",
        "TABLE DES TRAGÉDIES",
        "NOTES:",
        "FIN DU COMPLÉMENT DES VARIANTES.",
        "  [12] une note",
        "  [3-a] suite de la note",
        "[7]",
        "ELVIRE[246-a].",
        "_ital_",
        "Vers de douze                  14",
        "",
        "   ",
        "\r",
        "TRAGÉDIE",
        "1666",
        "text",
    ]
)
tome_like_text = st.lists(tome_fragment, max_size=40).map("\n".join)


@given(any_text)
def test_normalize_is_idempotent(text: str) -> None:
    once = cleaning.normalize(text)

    assert cleaning.normalize(once) == once


@given(any_text)
def test_clean_output_has_no_markup_or_stray_whitespace(text: str) -> None:
    out = cleaning.clean(text)

    assert "\r" not in out
    assert "_" not in out
    assert not note_ref.search(out)
    assert "\n\n\n" not in out
    assert not re.search(r"[ \t]$", out, re.MULTILINE)
    assert out == "" or (out.endswith("\n") and not out.endswith("\n\n"))


@given(any_text)
def test_clean_is_idempotent(text: str) -> None:
    once = cleaning.clean(text)

    assert cleaning.clean(once) == once


@given(any_text)
def test_drop_table_tail_keeps_a_prefix(text: str) -> None:
    assert text.startswith(cleaning.drop_table_tail(text))


@given(st.text(max_size=120))
def test_strip_verse_numbers_never_lengthens_a_line(line: str) -> None:
    out = cleaning.strip_verse_numbers(line)

    assert len(out) <= len(line)
    assert cleaning.strip_verse_numbers(out) == out


@given(body_text)
def test_extract_body_recovers_the_body_between_markers(body: str) -> None:
    raw = (
        "license\n*** START OF THE PROJECT GUTENBERG EBOOK X ***\n"
        f"{body}\n*** END OF THE PROJECT GUTENBERG EBOOK X ***\nfooter\n"
    )

    assert extract_body(raw) == f"{body}\n"


@given(any_text)
def test_build_tome_output_is_clean_for_any_body(body: str) -> None:
    marker = "*** {} OF THE PROJECT GUTENBERG EBOOK X ***"
    raw = f"x\n{marker.format('START')}\n{body}\n{marker.format('END')}\n"

    assert build_tome(raw) == cleaning.clean(f"{body}\n")


@given(any_text)
def test_describe_counts_match_the_text(text: str) -> None:
    stats = describe(text)

    assert stats.characters == len(text)
    assert stats.vocabulary == tuple(sorted(set(text)))
    assert stats.vocabulary_size == len(set(text))


@given(any_text)
def test_manifest_built_from_a_text_accepts_that_text(text: str) -> None:
    stats = describe(text)
    manifest = Manifest(
        name="tiny-corneille",
        sources=(),
        corpus=CorpusRecord(
            file="tiny_corneille.txt",
            sha256=sha256_hex(text.encode("utf-8")),
            characters=stats.characters,
            lines=stats.lines,
            vocabulary_size=stats.vocabulary_size,
        ),
    )

    assert check_corpus(manifest, text) == ()


@given(tome_like_text)
def test_clean_is_idempotent_on_tome_like_text(text: str) -> None:
    once = cleaning.clean(text)

    assert cleaning.clean(once) == once


@given(tome_like_text)
def test_clean_output_is_clean_on_tome_like_text(text: str) -> None:
    out = cleaning.clean(text)

    assert "\r" not in out
    assert "_" not in out
    assert not note_ref.search(out)
    assert not re.search(r"^\s*\[\d+(?:-[a-z])?\]", out, re.MULTILINE)
    assert "NOTICE." not in out
    assert "TABLE DES" not in out
