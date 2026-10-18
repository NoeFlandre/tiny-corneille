# Quality gates

Each gate must pass before a change is complete. Run them in this order.

| Order | Gate | Command | Pass condition |
| --- | --- | --- | --- |
| 1 | Format | `uv run ruff format --check .` | No file changes. |
| 2 | Lint | `uv run ruff check .` | No findings. |
| 3 | Types | `uv run ty check` | No diagnostics. |
| 4 | Tests | `uv run pytest --cov` | All tests pass. Coverage is at least 95%. |
| 5 | Architecture | `uv run lint-imports` | All contracts kept. |
| 6 | Complexity | `uv run coverage json -o coverage.json && uv run python scripts/crap.py coverage.json --max 6` | No function reaches a CRAP score of 6. |
| 7 | Mutation | `uv run mutmut run && uv run mutmut results` | No surviving or suspicious mutant. |
| 8 | Docs | `uv run mkdocs build --strict` | No warnings. |
| 9 | Smoke test | `uv run tiny-corneille --help` and a `build` on the fixtures | Exit code 0. |

## Lint rules

Ruff runs the rule families `E`, `W`, `F`, `I`, `B`, `UP`, `C90`, `N`, `SIM`, `RUF`, `PT`, `PERF`, `ANN` and `S`. Each family finds a class of defect.

- Cyclomatic complexity is at most 5 (`C901`).
- Tests may use `assert` and skip some annotations.
- The `mutants/` folder, which mutmut creates, is excluded.

## Test layers

- `tests/unit`: pure domain functions.
- `tests/property`: Hypothesis properties. The seed is fixed, so each run replays the same examples.
- `tests/integration`: adapters and the CLI, with fake downloads. No test reaches the network.
- `tests/acceptance`: the CLI as a subprocess, on fixtures.

## Complexity and CRAP

CRAP = complexity² × (1 − coverage)³ + complexity. A function with full coverage scores its complexity. The gate fails at 6 or above.

## Mutation testing

mutmut changes the code. Each change must break a test. A survivor means a test gap. Each survivor is either killed by a new test or marked as equivalent.

Lines that mutmut must not change carry `# pragma: no mutate`. Each such line is equivalent by construction:

- `encoding="UTF-8"` and `encode("UTF-8")`. Python treats the spelling as the same codec.
- A `None` initial value for a flag that is reset before use.
- A `None` default for a read that Python resolves the same way.
- A header name spelled with other capitals. urllib capitalises header names.
- A case-changed resource name. macOS file systems ignore case, so the change is invisible there. The Linux CI job still checks the real name.
- `blank_run = 0` in the title scan. The value is reset before it is read.

The mutation gate runs on Linux in CI.
