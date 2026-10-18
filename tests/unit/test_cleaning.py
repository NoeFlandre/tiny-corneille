from tiny_corneille.domain import cleaning


def test_normalize_converts_crlf_and_cr_to_lf() -> None:
    assert cleaning.normalize("a\r\nb\rc\n") == "a\nb\nc\n"


def test_normalize_composes_decomposed_accents() -> None:
    decomposed = "École"

    assert cleaning.normalize(decomposed) == "École"


def test_drop_front_matter_keeps_title_block_before_first_notice() -> None:
    text = "Grands écrivains\n\n\n\nMÉLITE\n\nCOMÉDIE\n\n1629\n\nNOTICE.\n\nNotice text.\n"

    assert (
        cleaning.drop_front_matter(text) == "MÉLITE\n\nCOMÉDIE\n\n1629\n\nNOTICE.\n\nNotice text.\n"
    )


def test_drop_front_matter_without_notice_keeps_text() -> None:
    assert cleaning.drop_front_matter("just text\n") == "just text\n"


def test_drop_front_matter_keeps_title_block_with_gap_before_notice() -> None:
    text = "Front\n\n\n\nAGÉSILAS\n\nTRAGÉDIE\n\n1666\n\n\n\n\nNOTICE.\n\nx\n"

    assert (
        cleaning.drop_front_matter(text) == "AGÉSILAS\n\nTRAGÉDIE\n\n1666\n\n\n\n\nNOTICE.\n\nx\n"
    )


def test_drop_apparatus_headings_removes_notes_headings_only() -> None:
    text = "Texte.\nNOTES:\nFin.\nFIN DU COMPLÉMENT DES VARIANTES.\n"

    assert cleaning.drop_apparatus_headings(text) == "Texte.\nFin.\n"


def test_remove_footnote_blocks_handles_letter_suffixed_notes() -> None:
    assert (
        cleaning.remove_footnote_blocks("Texte.\n\n[1602-a] Une note.\n\nSuite.\n")
        == "Texte.\n\n\nSuite.\n"
    )


def test_strip_inline_markers_removes_letter_suffixed_refs() -> None:
    assert cleaning.strip_inline_markers("ELVIRE[246-a].\n") == "ELVIRE.\n"


def test_drop_table_tail_cuts_at_first_table_heading() -> None:
    text = "Last play.\n\nTABLE DES TRAGÉDIES\nAgésilas\n"

    assert cleaning.drop_table_tail(text) == "Last play.\n"


def test_remove_editorial_notices_drops_notice_up_to_preface() -> None:
    text = "ACTE I\n\nNOTICE.\n\nEditor notes.\n\nAU LECTEUR.\n\nCorneille preface.\n"

    assert (
        cleaning.remove_editorial_notices(text) == "ACTE I\n\nAU LECTEUR.\n\nCorneille preface.\n"
    )


def test_remove_editorial_notices_drops_variant_list_up_to_actors() -> None:
    text = (
        "NOTICE.\nx\nLISTE DES ÉDITIONS QUI ONT ÉTÉ COLLATIONNÉES\n1666 in-12.\nACTEURS.\nHELENE.\n"
    )

    assert cleaning.remove_editorial_notices(text) == "ACTEURS.\nHELENE.\n"


def test_remove_footnote_blocks_drops_note_and_its_continuation() -> None:
    text = "Texte.\n\n  [1] Une note.\n  suite de la note.\n\nSuite.\n"

    assert cleaning.remove_footnote_blocks(text) == "Texte.\n\n\nSuite.\n"


def test_strip_inline_markers_removes_note_refs_and_italics() -> None:
    text = "ACTEURS[11]. Il_ dit _ceci_ à Parfait[1].\n"

    assert cleaning.strip_inline_markers(text) == "ACTEURS. Il dit ceci à Parfait.\n"


def test_strip_verse_numbers_removes_trailing_line_numbers() -> None:
    line = "    Ce me doit être assez qu'en secret il soupire,                15"

    assert (
        cleaning.strip_verse_numbers(line) == "    Ce me doit être assez qu'en secret il soupire,"
    )


def test_strip_verse_numbers_keeps_years_and_single_spaced_numbers() -> None:
    assert cleaning.strip_verse_numbers("    1666") == "    1666"
    assert cleaning.strip_verse_numbers("Tome 7 en 1666") == "Tome 7 en 1666"


def test_tidy_collapses_spaces_and_blank_runs() -> None:
    text = "\n\n  a   b  \n\n\n\n c \n\n"

    assert cleaning.tidy(text) == "a b\n\nc\n"


def test_clean_applies_every_rule_in_order() -> None:
    text = (
        "Grands écrivains\n\n\n\n"
        "AGÉSILAS\n\nTRAGÉDIE\n\n1666\n\n"
        "NOTICE.\n\nEditor note[1].\n\n"
        "AU LECTEUR.\n\nPreface.\n\n"
        "ACTEURS[2].\n\nAGÉSILAS.\n\n"
        "  [1] A note.\n  continued.\n\n"
        "Ce vers finit ici.                 5\n\n"
        "TABLE DES TRAGÉDIES\nAgésilas\n"
    )

    assert cleaning.clean(text) == (
        "AGÉSILAS\n\nTRAGÉDIE\n\n1666\n\n"
        "AU LECTEUR.\n\nPreface.\n\n"
        "ACTEURS.\n\nAGÉSILAS.\n\n"
        "Ce vers finit ici.\n"
    )
