# ADR 0006: Complexity and CRAP as guardrails

## Context

Complex functions are hard to read and hard to test. A coverage number alone does not show this.

## Decision

- Ruff fails any function with cyclomatic complexity above 5.
- `scripts/crap.py` fails any function with a CRAP score of 6 or above.
- The guardrails stop a bad change. Refactor a module when its duties are mixed. Do not refactor only to lower a number.

## Consequences

- With full coverage, the CRAP score equals the complexity. The limit of 5 keeps every function below 6.
