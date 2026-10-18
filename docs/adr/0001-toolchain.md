# ADR 0001: Toolchain

## Context

The project needs one way to install, lint, type-check, test and mutate the code.

## Decision

- uv manages the environment and the lock file.
- ruff formats and lints the code.
- ty checks the types.
- pytest runs the tests. Hypothesis adds property tests.
- mutmut runs the mutation tests.
- import-linter checks the architecture.
- coverage measures the test coverage. The CRAP check is in `scripts/crap.py`.

## Consequences

- One command installs everything: `uv sync --locked`.
- ty is before version 1.0. Its results can change between releases. The lock file pins the version.
