# ADR 0004: Manifest and hosting

## Context

Each run must produce the same corpus. A reader must be able to check the data.

## Decision

- `src/tiny_corneille/corpus_manifest.json` pins the SHA-256 of each raw tome. It also pins the corpus checksum and its statistics.
- `fetch` refuses any download that does not match its pinned checksum.
- Code lives in the GitHub repository.
- Data lives in the Hugging Face dataset repository. The dataset holds the corpus, the manifest and a dataset card.

## Consequences

- The repository stays small. No data file is committed.
- A release step updates the corpus record. See [Data](../data.md).
