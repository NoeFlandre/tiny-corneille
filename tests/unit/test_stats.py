from tiny_corneille.domain.stats import describe


def test_describe_counts_characters_lines_and_vocabulary() -> None:
    stats = describe("ab\nc")

    assert stats.characters == 4
    assert stats.lines == 2
    assert stats.vocabulary == ("\n", "a", "b", "c")
    assert stats.vocabulary_size == 4


def test_describe_empty_text_has_no_lines_or_vocabulary() -> None:
    stats = describe("")

    assert stats.characters == 0
    assert stats.lines == 0
    assert stats.vocabulary == ()
