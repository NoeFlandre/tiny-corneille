"""Fail when a function reaches the CRAP threshold.

CRAP = complexity^2 * (1 - coverage)^3 + complexity (Savoia and Evans, 2007).
Complexity comes from radon; coverage comes from a coverage.py JSON report.

Usage, from the project root:
    uv run coverage json -o coverage.json
    uv run python scripts/crap.py coverage.json --max 6
"""

import argparse
import json
import sys
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from radon.complexity import cc_visit


@dataclass(frozen=True)
class Row:
    name: str
    location: str
    complexity: int
    coverage: float
    score: float


def crap_score(complexity: int, coverage: float) -> float:
    return complexity**2 * (1 - coverage) ** 3 + complexity


def function_coverage(file_data: dict[str, Any], first_line: int, last_line: int) -> float:
    """Share of the function's executable lines that ran; 1.0 when it has none."""
    span = range(first_line, last_line + 1)
    executed = sum(1 for line in file_data["executed_lines"] if line in span)
    missing = sum(1 for line in file_data["missing_lines"] if line in span)
    total = executed + missing
    return executed / total if total else 1.0


def _file_rows(path: Path, file_data: dict[str, Any]) -> Iterator[Row]:
    for block in cc_visit(path.read_text(encoding="utf-8")):
        for function in getattr(block, "methods", [block]):
            coverage = function_coverage(file_data, function.lineno, function.endline)
            yield Row(
                name=function.name,
                location=f"{path.as_posix()}:{function.lineno}",
                complexity=function.complexity,
                coverage=coverage,
                score=crap_score(function.complexity, coverage),
            )


def _rows(source: Path, report: dict[str, Any]) -> Iterator[Row]:
    for path in sorted(source.rglob("*.py")):
        if path.as_posix() not in report:
            raise SystemExit(f"no coverage data for {path.as_posix()}")
        yield from _file_rows(path, report[path.as_posix()])


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check CRAP scores against a threshold.")
    parser.add_argument("coverage", type=Path, help="coverage.py JSON report")
    parser.add_argument("--max", type=float, default=6.0, dest="threshold", help="fail at or above")
    parser.add_argument("--source", type=Path, default=Path("src"), help="source tree to score")
    args = parser.parse_args(argv)

    report = json.loads(args.coverage.read_text(encoding="utf-8"))["files"]
    rows = sorted(_rows(args.source, report), key=lambda row: -row.score)
    for row in rows[:10]:
        coverage = f"{row.coverage:.0%}"
        print(f"{row.score:7.2f}  cc={row.complexity}  cov={coverage}  {row.location} {row.name}")
    offenders = [row for row in rows if row.score >= args.threshold]
    if offenders:
        print(
            f"CRAP check failed: {len(offenders)} function(s) at or above {args.threshold}",
            file=sys.stderr,
        )
        return 1
    print(f"CRAP check passed: {len(rows)} functions, all below {args.threshold}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
