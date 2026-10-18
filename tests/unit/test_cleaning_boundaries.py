from tiny_corneille.domain import cleaning


def test_title_block_directly_above_the_notice_is_kept() -> None:
    text = "Front\n\n\n\nTITLE\nNOTICE.\nx\n"

    assert cleaning.drop_front_matter(text) == "TITLE\nNOTICE.\nx\n"


def test_gap_of_two_blank_lines_does_not_separate_front_matter() -> None:
    text = "Front\n\n\nTITLE\n\nNOTICE.\n"

    assert cleaning.drop_front_matter(text) == text


def test_title_block_at_the_top_of_the_text_is_kept_whole() -> None:
    text = "TITLE\n\nNOTICE.\n"

    assert cleaning.drop_front_matter(text) == text


def test_notice_on_the_first_line_keeps_the_text() -> None:
    assert cleaning.drop_front_matter("NOTICE.\nx\n") == "NOTICE.\nx\n"


def test_long_gap_adjacent_to_the_notice_is_not_a_separator() -> None:
    text = "Front\n\n\n\nTITLE\n\n\n\n\nNOTICE.\n"

    assert cleaning.drop_front_matter(text) == "TITLE\n\n\n\n\nNOTICE.\n"


def test_tidy_keeps_letters_that_look_like_strip_characters() -> None:
    assert cleaning.tidy("XAX\nXB\n") == "XAX\nXB\n"


def test_tidy_of_empty_or_blank_text_is_empty() -> None:
    assert cleaning.tidy("") == ""
    assert cleaning.tidy("\n\n  \n") == ""
