# Technical debt

Each item says what is weak, why it exists, and how to clean it up. Counts come from the release corpus.

## 1. Editorial text remains in the corpus

- Weakness: 31 lines start with a square bracket. Most are verses that later editions dropped. The editor marks them with brackets and edition dates, and 24 lines carry such a date. A further 49 lines start with `--`. They are paragraphs of editor notes that lost their note marker. Two passages of editor prose remain: an analysis in tome 3 (`Toutes ces enluminures`) and a list heading in tome 6 (`LISTE DES TRAGÉDIES`).
- Why: each form needs its own rule, and each rule risks removing Corneille's words. The residue is small against 3.8 million characters.
- Cleanup: check the `--` lines by hand, then add a rule for each form that is clearly editorial. Add a fixture for each rule.

## 2. Notes whose paragraphs are not indented like a note

- Weakness: a note goes on past a blank line only when the next text line has exactly two spaces of indent. A verse quotation inside a note has more indent, so it ends the note and leaks into the corpus.
- Why: the seven tomes indent notes this way, and the rule uses that layout. A rule that reads note text by its content would be less exact.
- Cleanup: a note ends at the next note number or at a clear start of play text. Test it on the release corpus.

## 3. The cleaning rules fit the Marty-Laveaux layout

- Weakness: other editions of Corneille use other layouts, and the rules would need new cases.
- Why: the project targets one edition.
- Cleanup: add one rule per layout and a fixture for each.

## 4. Front matter in tome 1 depends on the AVERTISSEMENTS heading

- Weakness: the corpus starts at the `AVERTISSEMENTS` heading of tome 1. A tome without that heading falls back to the title block above the first notice. A tome without a notice keeps its front matter.
- Why: the seven tomes use this layout. A general rule was not needed.
- Cleanup: detect the first work title in another way, and add a fixture for a tome without notices.

## 5. Some verse lines keep a printed line number

- Weakness: a line number after one space is not removed. A few lines keep one.
- Why: the rule removes numbers after two or more spaces. A rule for one space would also remove real words.
- Cleanup: check the remaining lines by hand and add exceptions.

## 6. The real corpus is not checked in CI

- Weakness: CI tests the fixtures only. The release corpus is checked by hand with `fetch`, `build` and `verify`.
- Why: the real download needs the network, and CI must stay deterministic.
- Cleanup: add a scheduled job that fetches and verifies the corpus.

## 7. The manifest update is manual

- Weakness: `scripts/pin_corpus.py` has no test.
- Why: it runs once per release.
- Cleanup: move it into the CLI and test it.

## 8. Some mutants are equivalent on one platform only

- Weakness: a case change in a file name survives on macOS. It is caught on Linux.
- Why: macOS file systems ignore case.
- Cleanup: none planned. The mutation gate runs on Linux.

## 9. The Docker image is not built in this environment

- Weakness: no container engine was available for the release. The Dockerfile steps were replayed in a clean copy. The image itself has not been built or run.
- Why: no Docker Desktop or OrbStack is installed on the release machine.
- Cleanup: the CI job builds and runs the image. Run it once before a release.

## 10. The Docker image is tested on one architecture

- Weakness: only the build host's architecture is tested.
- Why: multi-architecture builds need a more complex CI setup.
- Cleanup: build for `linux/amd64` and `linux/arm64` in CI.
