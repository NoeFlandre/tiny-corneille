from tiny_corneille.domain.corpus import build_corpus, build_tome

START = "*** START OF THE PROJECT GUTENBERG EBOOK TEST ***"
END = "*** END OF THE PROJECT GUTENBERG EBOOK TEST ***"


def _raw(body: str) -> str:
    return f"license\n{START}\n{body}\n{END}\nfooter\n"


def test_build_tome_strips_boilerplate_and_cleans_the_body() -> None:
    raw = _raw(
        "Front\n\n\n\nMÉLITE\n\nCOMÉDIE\n\n1629\n\nNOTICE.\n\nNote[1].\n\nAU LECTEUR.\n\nPreface."
    )

    assert build_tome(raw) == "MÉLITE\n\nCOMÉDIE\n\n1629\n\nAU LECTEUR.\n\nPreface.\n"


def test_build_corpus_joins_tomes_in_order_with_a_blank_line() -> None:
    first = _raw("ONE\n\nTRAGÉDIE")
    second = _raw("TWO\n\nCOMÉDIE")

    assert build_corpus([first, second]) == "ONE\n\nTRAGÉDIE\n\nTWO\n\nCOMÉDIE\n"
