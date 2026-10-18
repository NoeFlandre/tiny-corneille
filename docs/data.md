# Data

## Sources

The corpus uses the seven tomes of the Marty-Laveaux edition. Project Gutenberg publishes them.

| Tome | Gutenberg id |
| --- | --- |
| 1 | 31628 |
| 2 | 34445 |
| 3 | 36011 |
| 4 | 39739 |
| 5 | 46527 |
| 6 | 48590 |
| 7 | 51612 |

The manifest pins the SHA-256 of each raw download. `fetch` refuses a file that does not match.

## Cleaning rules

The rules keep the words of Corneille. They remove the material that is not his text.

Removed:

- The Gutenberg header and footer.
- The editor's front matter. In tome 1, this covers the title pages, the editor's biography, the chronological table and the list of works. It ends where Corneille's own prefaces begin.
- Editor notices, which start at a `NOTICE.` heading. A notice ends at the first preface, examination or list of characters.
- Lists of collated editions (`LISTE DES ÉDITIONS`) and variant complements (`COMPLÉMENT DES VARIANTES`).
- Editorial footnotes and their references, such as `[12]`, `[246-a]` and `[1025-b:`. A note also covers the indented paragraphs that follow it.
- Tables of contents at the end of each tome.
- Printed line numbers at the end of verse lines.
- Italic markers (underscores).

Kept:

- Plays, with their stage directions and character lists.
- Corneille's own prefaces and discourses, including the `AVERTISSEMENTS` of tome 1 and the `Discours` that follow them.
- Corneille's examinations (`EXAMEN`) and prefaces (`PRÉFACE`) that follow a notice.

Other rules:

- Line endings become LF.
- Text is in Unicode NFC form.
- Original spelling stays. The corpus does not modernise words.
- Runs of spaces become one space.
- Runs of blank lines become one blank line.

## Known residue

Some editorial text remains. [Technical debt](tech-debt.md) lists it, with the counts measured on the release corpus.

## Output

`tiny_corneille.txt` is UTF-8. The seven cleaned tomes follow each other in order. One blank line separates two tomes.

The corpus holds 1,571,834 GPT-2 tokens, measured with the tiktoken `gpt2` encoding by `scripts/count_gpt2_tokens.py`.

The manifest records the expected statistics. `verify` compares the corpus with them, byte for byte.
