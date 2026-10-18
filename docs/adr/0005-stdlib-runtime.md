# ADR 0005: Standard library at run time

## Context

The tool runs on a researcher's machine and in Docker. Fewer dependencies mean fewer failures.

## Decision

- The package has no run-time dependencies.
- The command line uses `argparse`. Downloads use `urllib`.
- Development tools are in the `dev` and `docs` dependency groups.

## Consequences

- The Docker image installs only the package itself.
- The command line does not offer shell completion or colour.
