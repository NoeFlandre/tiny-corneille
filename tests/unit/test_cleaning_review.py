from tiny_corneille.domain import cleaning


def test_front_matter_keeps_corneilles_own_prefaces_before_the_first_notice() -> None:
    text = (
        "Editor front matter\n\n\n\n"
        "AVERTISSEMENTS\nPLACÉS PAR CORNEILLE\n\nAU LECTEUR.\n\nPreface.\n\n\n\n"
        "MÉLITE\n\nCOMÉDIE\n\n1629\n\nNOTICE.\n\nx\n"
    )

    assert cleaning.drop_front_matter(text) == (
        "AVERTISSEMENTS\nPLACÉS PAR CORNEILLE\n\nAU LECTEUR.\n\nPreface.\n\n\n\n"
        "MÉLITE\n\nCOMÉDIE\n\n1629\n\nNOTICE.\n\nx\n"
    )


def test_notice_block_ends_at_corneilles_examen() -> None:
    text = "NOTICE.\nEditor notes.\n\nEXAMEN.\nCorneille's own examination.\n\nACTEURS.\nHELENE.\n"

    assert cleaning.remove_editorial_notices(text) == (
        "EXAMEN.\nCorneille's own examination.\n\nACTEURS.\nHELENE.\n"
    )


def test_notice_block_ends_at_corneilles_preface() -> None:
    text = "NOTICE.\nEditor notes.\nPRÉFACE.\nCorneille's preface.\n"

    assert cleaning.remove_editorial_notices(text) == "PRÉFACE.\nCorneille's preface.\n"


def test_list_block_matches_the_plural_heading() -> None:
    text = "LISTES DES ÉDITIONS QUI ONT ÉTÉ COLLATIONNÉES\n1666 in-12.\nACTEURS.\nHELENE.\n"

    assert cleaning.remove_editorial_notices(text) == "ACTEURS.\nHELENE.\n"


def test_variant_complement_block_is_removed_up_to_its_end_line() -> None:
    text = (
        "Texte.\n\nCOMPLÉMENT DES VARIANTES.\nVariant text.\n\n"
        "FIN DU COMPLÉMENT DES VARIANTES.\nSuite.\n"
    )

    assert cleaning.clean(text) == "Texte.\n\nSuite.\n"


def test_note_continues_over_a_blank_line_into_an_indented_paragraph() -> None:
    text = "Texte.\n\n  [1] Une note.\n\n  suite de la note.\n\nSuite.\n"

    assert cleaning.remove_footnote_blocks(text) == "Texte.\n\n\nSuite.\n"


def test_note_ends_at_a_blank_line_before_unindented_text() -> None:
    text = "  [1] Une note.\n\nSuite du texte.\n"

    assert cleaning.remove_footnote_blocks(text) == "\nSuite du texte.\n"
