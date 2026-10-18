"""Locate the body of a Project Gutenberg text between its boilerplate markers."""

import re


class BoilerplateError(ValueError):
    """A Project Gutenberg start or end marker is missing."""


_START = re.compile(r"^\*{3} ?START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\n", re.MULTILINE)
_END = re.compile(r"^\*{3} ?END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK", re.MULTILINE)


def extract_body(raw: str) -> str:
    """Return the text strictly between the START and END marker lines."""
    start = _START.search(raw)
    if start is None:
        raise BoilerplateError("START marker not found")
    end = _END.search(raw, start.end())
    if end is None:
        raise BoilerplateError("END marker not found")
    return raw[start.end() : end.start()]
