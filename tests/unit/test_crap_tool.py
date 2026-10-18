import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

_SCRIPT = Path(__file__).parents[2] / "scripts" / "crap.py"


@pytest.fixture
def crap_tool() -> ModuleType:
    spec = importlib.util.spec_from_file_location("crap", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fully_covered_function_scores_its_complexity(crap_tool: ModuleType) -> None:
    assert crap_tool.crap_score(complexity=5, coverage=1.0) == 5


def test_uncovered_function_is_penalised_by_complexity_squared(crap_tool: ModuleType) -> None:
    assert crap_tool.crap_score(complexity=5, coverage=0.0) == 30
    assert crap_tool.crap_score(complexity=1, coverage=0.0) == 2


def test_coverage_of_a_function_counts_only_its_own_lines(crap_tool: ModuleType) -> None:
    coverage = {"executed_lines": [10, 11, 40], "missing_lines": [12, 41]}

    value = crap_tool.function_coverage(coverage, first_line=10, last_line=12)

    assert value == pytest.approx(2 / 3)


def test_function_without_executable_lines_counts_as_covered(crap_tool: ModuleType) -> None:
    assert crap_tool.function_coverage({"executed_lines": [], "missing_lines": []}, 1, 2) == 1.0
