import runpy
import sys

import pytest


def test_python_dash_m_runs_the_cli_and_exits_with_its_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "argv", ["tiny-corneille", "--version"])

    with pytest.raises(SystemExit) as info:
        runpy.run_module("tiny_corneille", run_name="__main__")

    assert info.value.code == 0
