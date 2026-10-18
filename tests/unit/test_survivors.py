from tiny_corneille.domain import cleaning


def test_note_ends_at_the_end_of_the_text_and_keeps_trailing_blank_lines() -> None:
    assert cleaning.remove_footnote_blocks("  [1] Une note.\n\n") == "\n"
