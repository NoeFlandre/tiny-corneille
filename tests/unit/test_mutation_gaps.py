from tiny_corneille.domain import cleaning
from tiny_corneille.domain.gutenberg import extract_body


def test_text_without_separator_or_trailing_newline_is_returned_unchanged() -> None:
    assert cleaning.drop_front_matter("Title\nNOTICE.") == "Title\nNOTICE."


def test_end_marker_before_the_start_marker_is_ignored() -> None:
    raw = (
        "*** END OF THE PROJECT GUTENBERG EBOOK X ***\n"
        "*** START OF THE PROJECT GUTENBERG EBOOK X ***\n"
        "body\n"
        "*** END OF THE PROJECT GUTENBERG EBOOK X ***\n"
    )

    assert extract_body(raw) == "body\n"
