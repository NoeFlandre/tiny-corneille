---
language:
- fr
license: other
license_name: public-domain-project-gutenberg
pretty_name: Tiny Corneille
task_categories:
- text-generation
tags:
- french
- literature
- corneille
- character-level
- project-gutenberg
---

# Tiny Corneille

Tiny Corneille is a clean French text corpus. It holds the seven tomes of the works of Pierre Corneille, from Project Gutenberg. The corpus follows the idea of Andrej Karpathy's tiny Shakespeare.

- **Code, rules and reproduction:** [github.com/NoeFlandre/tiny-corneille](https://github.com/NoeFlandre/tiny-corneille)

## Files

- `tiny_corneille.txt`: the corpus. UTF-8, LF line endings, 3,795,595 characters, 118,402 lines, 119 distinct characters, and 1,571,834 GPT-2 tokens (2.415 characters per token, tiktoken `gpt2` encoding).
- `manifest.json`: the SHA-256 of each raw tome and of the corpus, and the expected statistics.

## Sources

The tomes come from the edition of Charles Joseph Marty-Laveaux, as published by Project Gutenberg.

| Tome | Gutenberg id |
| --- | --- |
| 1 | [31628](https://www.gutenberg.org/ebooks/31628) |
| 2 | [34445](https://www.gutenberg.org/ebooks/34445) |
| 3 | [36011](https://www.gutenberg.org/ebooks/36011) |
| 4 | [39739](https://www.gutenberg.org/ebooks/39739) |
| 5 | [46527](https://www.gutenberg.org/ebooks/46527) |
| 6 | [48590](https://www.gutenberg.org/ebooks/48590) |
| 7 | [51612](https://www.gutenberg.org/ebooks/51612) |

## Processing

The rules keep Corneille's words and remove the rest:

- Removed: the Gutenberg header and footer, the editor's front matter, editor notices, lists of collated editions, variant complements, editorial footnotes and their references, tables of contents, printed verse line numbers, and italic markers.
- Kept: the plays with their stage directions and character lists, Corneille's own prefaces and discourses (including the `AVERTISSEMENTS` of tome 1), and his examinations.
- Original spelling is kept.
- Known residue: some editorial text remains, such as bracketed variant verses and a few editor paragraphs. The data notes list it.

The full rules are in the [data notes](https://github.com/NoeFlandre/tiny-corneille/blob/main/docs/data.md).

## Reproduce

```bash
git clone https://github.com/NoeFlandre/tiny-corneille
cd tiny-corneille
uv sync --locked
uv run tiny-corneille fetch
uv run tiny-corneille build
uv run tiny-corneille verify
```

`fetch` checks each raw download against `manifest.json`. `verify` checks the built corpus byte for byte.

## Licence

The works of Corneille are in the public domain. Project Gutenberg publishes the ebooks under its own terms, including its trademark notice. Keep that notice when you redistribute this data.
