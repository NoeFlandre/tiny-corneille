# Tiny Corneille

Tiny Corneille is a French text corpus. It contains the seven tomes of the works of Pierre Corneille, from Project Gutenberg. The corpus follows the idea of Andrej Karpathy's tiny Shakespeare.

- Code: [github.com/NoeFlandre/tiny-corneille](https://github.com/NoeFlandre/tiny-corneille)
- Data: [huggingface.co/datasets/NoeFlandre/tiny-corneille](https://huggingface.co/datasets/NoeFlandre/tiny-corneille)

## What the tool does

1. It downloads the seven raw tomes.
2. It checks the SHA-256 of each tome.
3. It removes the Gutenberg text and the editorial notes.
4. It writes one corpus file.
5. It checks the corpus file against the manifest.

Read [Usage](usage.md) to run the tool.
