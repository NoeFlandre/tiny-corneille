"""Character-level statistics of a corpus."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CorpusStats:
    """Counts and character vocabulary of a corpus."""

    characters: int
    lines: int
    vocabulary: tuple[str, ...]

    @property
    def vocabulary_size(self) -> int:
        return len(self.vocabulary)


def describe(text: str) -> CorpusStats:
    """Describe a text by its length, line count and sorted character set."""
    return CorpusStats(
        characters=len(text),
        lines=len(text.splitlines()),
        vocabulary=tuple(sorted(set(text))),
    )
