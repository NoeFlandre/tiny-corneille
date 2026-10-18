import pytest

from tiny_corneille.domain.gutenberg import BoilerplateError, extract_body

START = "*** START OF THE PROJECT GUTENBERG EBOOK ŒUVRES DE P. CORNEILLE, TOME 07 ***"
END = "*** END OF THE PROJECT GUTENBERG EBOOK ŒUVRES DE P. CORNEILLE, TOME 07 ***"


def test_extract_body_returns_text_between_markers() -> None:
    raw = f"license header\n{START}\nAGÉSILAS\nTRAGÉDIE\n{END}\nlicense footer\n"

    assert extract_body(raw) == "AGÉSILAS\nTRAGÉDIE\n"


def test_extract_body_accepts_crlf_line_endings() -> None:
    raw = f"head\r\n{START}\r\nVers un\r\n{END}\r\ntail\r\n"

    assert extract_body(raw) == "Vers un\r\n"


def test_extract_body_accepts_this_project_variant() -> None:
    raw = (
        "*** START OF THIS PROJECT GUTENBERG EBOOK TEST ***\n"
        "body\n"
        "*** END OF THIS PROJECT GUTENBERG EBOOK TEST ***\n"
    )

    assert extract_body(raw) == "body\n"


def test_extract_body_without_start_marker_raises() -> None:
    with pytest.raises(BoilerplateError, match="START"):
        extract_body(f"no start here\n{END}\n")


def test_extract_body_without_end_marker_raises() -> None:
    with pytest.raises(BoilerplateError, match="END"):
        extract_body(f"{START}\nbody only\n")
