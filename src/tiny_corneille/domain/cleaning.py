"""Pure text rules that turn a Gutenberg tome body into corpus text.

Each rule is one small function. clean() fixes their order.
"""

import re
import unicodedata
from collections.abc import Iterable

_TITLE_GAP = 3
_NOTICE_HEADING = "NOTICE."
_CORNEILLE_PREFACES = "AVERTISSEMENTS"
_TABLE_HEADING = "TABLE DES"
_APPARATUS_HEADINGS = frozenset({"NOTES:", "FOOTNOTES:", "FIN DU COMPLÉMENT DES VARIANTES."})
# An editorial block starts on a heading and ends at the first line of Corneille's own text.
_BLOCK_STARTS = (
    (re.compile(r"NOTICE\."), ("AU LECTEUR", "ACTEURS", "EXAMEN", "PRÉFACE")),
    (re.compile(r"LISTES? DES ÉDITIONS.*"), ("ACTEURS",)),
    (re.compile(r"COMPLÉMENT(?: DES VARIANTES\.)?"), ("FIN DU COMPLÉMENT DES VARIANTES.",)),
)
_NOTE_NUMBER = r"\[\d+(?:-[a-z])?"
_FOOTNOTE = re.compile(rf"^\s*{_NOTE_NUMBER}[\]:]\s")
_NOTE_INDENT = re.compile(r"^ {2}\S")
_NOTE_REF = re.compile(rf"{_NOTE_NUMBER}\]")
_VERSE_NUMBER = re.compile(r"(?<=\S)\s{2,}\d{1,4}\s*$")


def normalize(text: str) -> str:
    """Use LF line endings and composed Unicode characters."""
    return unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))


def drop_front_matter(text: str) -> str:
    """Keep Corneille's own prefaces and the first work, drop the editor's front matter.

    The tomes that open with Corneille's prefaces start at the AVERTISSEMENTS heading.
    The others start at the title block above the first notice.
    """
    lines = text.split("\n")
    notice = _notice_index(lines)
    if notice is None:
        return text
    preface = _preface_index(lines, notice)
    if preface is not None:
        return "\n".join(lines[preface:])
    top = _title_top(lines, notice)
    return text if top is None else "\n".join(lines[top:])  # pragma: no mutate


def _notice_index(lines: list[str]) -> int | None:
    return next((i for i, line in enumerate(lines) if line.strip() == _NOTICE_HEADING), None)


def _preface_index(lines: list[str], notice: int) -> int | None:
    return next((i for i in range(notice) if lines[i].strip() == _CORNEILLE_PREFACES), None)


def _title_top(lines: list[str], notice: int) -> int | None:
    """Topmost line of the title block above the notice, or None when there is none.

    The title block is the run of text lines above the notice that is not
    separated from the notice by a gap of at least _TITLE_GAP blank lines.
    """
    top: int | None = None
    blank_run = 0  # pragma: no mutate
    for index in range(notice - 1, -1, -1):
        if not lines[index].strip():
            blank_run += 1
        elif _is_separator(top, blank_run):
            break
        else:
            top = index
            blank_run = 0
    return top


def _is_separator(top: int | None, blank_run: int) -> bool:
    return top is not None and blank_run >= _TITLE_GAP


def drop_table_tail(text: str) -> str:
    """Remove the table of contents at the end of a tome."""
    lines = text.split("\n")
    for index, line in enumerate(lines):
        if line.strip().startswith(_TABLE_HEADING):
            return "\n".join(lines[:index])
    return text


def remove_editorial_notices(text: str) -> str:
    """Remove editor notices, variant lists and variant complements; keep Corneille's own text."""
    kept: list[str] = []
    stops: tuple[str, ...] | None = None
    for line in text.split("\n"):
        stripped = line.strip()
        if stops is None:
            stops = _block_stops(stripped)
            if stops is None:
                kept.append(line)
        elif stripped.startswith(stops):
            stops = None
            kept.append(line)
    return "\n".join(kept)


def _block_stops(stripped: str) -> tuple[str, ...] | None:
    for start, stops in _BLOCK_STARTS:
        if start.fullmatch(stripped):
            return stops
    return None


def drop_apparatus_headings(text: str) -> str:
    """Remove headings that announce editorial notes but carry no text."""
    return "\n".join(line for line in text.split("\n") if line.strip() not in _APPARATUS_HEADINGS)


def remove_footnote_blocks(text: str) -> str:
    """Remove editorial footnotes: a note line and the paragraphs indented like it."""
    lines = text.split("\n")
    kept: list[str] = []
    in_note = False  # pragma: no mutate
    for index in range(len(lines)):
        in_note = _next_in_note(in_note, lines, index)
        if not in_note:
            kept.append(lines[index])
    return "\n".join(kept)


def _next_in_note(in_note: bool, lines: list[str], index: int) -> bool:
    line = lines[index]
    if _FOOTNOTE.match(line):
        return True
    if line.strip():
        return in_note
    return in_note and _note_continues(lines, index)


def _note_continues(lines: list[str], blank_index: int) -> bool:
    """A note goes on past a blank line when the next text line is indented like a note."""
    for line in lines[blank_index + 1 :]:
        if line.strip():
            return _NOTE_INDENT.match(line) is not None
    return False


def strip_inline_markers(text: str) -> str:
    """Remove inline note references and italic underscores."""
    return _NOTE_REF.sub("", text).replace("_", "")


def strip_verse_numbers(line: str) -> str:
    """Remove the printed line number at the end of a verse line."""
    return _VERSE_NUMBER.sub("", line)


def tidy(text: str) -> str:
    """Collapse spaces, keep at most one blank line, end with one newline."""
    lines = [" ".join(line.split()) for line in text.split("\n")]
    body = "\n".join(_collapse_blank_runs(lines)).strip("\n")  # pragma: no mutate
    return f"{body}\n" if body else ""


def _collapse_blank_runs(lines: Iterable[str]) -> list[str]:
    kept: list[str] = []
    for line in lines:
        if line == "" and (not kept or kept[-1] == ""):
            continue
        kept.append(line)
    return kept


def clean(text: str) -> str:
    """Apply every cleaning rule in order."""
    text = normalize(text)
    text = drop_front_matter(text)
    text = drop_table_tail(text)
    text = remove_editorial_notices(text)
    text = drop_apparatus_headings(text)
    text = remove_footnote_blocks(text)
    text = strip_inline_markers(text)
    text = "\n".join(strip_verse_numbers(line) for line in text.split("\n"))
    return tidy(text)
