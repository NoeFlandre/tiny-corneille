# ADR 0002: Pure domain core

## Context

Cleaning and checking the text must be easy to test. File access and network access make tests slow and fragile.

## Decision

- `tiny_corneille.domain` holds pure functions only. It has no file, network or console access.
- `tiny_corneille.adapters` holds the file and network code.
- `tiny_corneille.cli` wires the two together.
- import-linter enforces these rules in `pyproject.toml`.

## Consequences

- Most tests run without fixtures on disk.
- The domain modules do not import each other in a cycle. The `acyclic_siblings` contract checks this.
