from tiny_corneille.domain import cleaning


def test_footnote_with_a_colon_after_its_number_is_removed() -> None:
    text = "Texte.\n\n[1025-b: Voltaire donne ces huit vers.\n  suite de la note.\n\nSuite.\n"

    assert cleaning.remove_footnote_blocks(text) == "Texte.\n\n\nSuite.\n"
