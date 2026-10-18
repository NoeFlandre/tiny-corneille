# Usage

The tool has three commands. Run them from the project root.

## Commands

| Command | Purpose |
| --- | --- |
| `fetch` | Download the seven raw tomes. Check each checksum. |
| `build` | Clean the raw tomes. Write one corpus file. |
| `verify` | Check a corpus file against the manifest. |

## Run the full pipeline

```bash
uv run tiny-corneille fetch
uv run tiny-corneille build
uv run tiny-corneille verify
```

Raw tomes go to `data/raw/`. The corpus goes to `data/tiny_corneille.txt`.

## Options

Run `tiny-corneille COMMAND --help` for the full list.

- `fetch --output-dir PATH`: where to write the raw tomes.
- `fetch --manifest PATH`: a manifest file. The default is the packaged manifest.
- `build --input-dir PATH`: where the raw tomes are.
- `build --output PATH`: the corpus file to write.
- `verify --corpus PATH`: the corpus file to check.
- `verify --manifest PATH`: a manifest file. The default is the packaged manifest.

`build` prints a JSON summary. The summary holds `sha256`, `characters`, `lines` and `vocabulary_size`.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Success. |
| 1 | A checksum, manifest or corpus check failed, or an input file is not valid. |
| 2 | The command line is wrong. |
| 3 | A network, file or path problem stopped the command. This includes a write that failed during `fetch`. The output directory may then mix tomes from two runs. |

## Docker

```bash
docker build -t tiny-corneille .
docker run --rm -v "$PWD/data:/work/data" tiny-corneille fetch
docker run --rm -v "$PWD/data:/work/data" tiny-corneille build
docker run --rm -v "$PWD/data:/work/data" tiny-corneille verify
```
