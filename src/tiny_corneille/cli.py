"""Command-line interface: fetch the raw tomes, build the corpus, verify it.

Exit codes:
    0  success
    1  a checksum, manifest or corpus check failed
    2  usage error (reported by argparse)
    3  environment problem: network failure, missing file, unreadable path
"""

import argparse
import json
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from tiny_corneille import __version__
from tiny_corneille.adapters import filesystem, network
from tiny_corneille.domain.corpus import build_corpus
from tiny_corneille.domain.gutenberg import BoilerplateError
from tiny_corneille.domain.manifest import (
    Manifest,
    ManifestError,
    Source,
    check_corpus,
    parse_manifest,
    sha256_hex,
    source_problem,
)
from tiny_corneille.domain.stats import describe

EXIT_OK = 0
EXIT_CHECK_FAILED = 1
EXIT_ENVIRONMENT = 3

DEFAULT_RAW_DIR = Path("data/raw")
DEFAULT_CORPUS = Path("data/tiny_corneille.txt")


@dataclass(frozen=True)
class CliError(Exception):
    code: int
    message: str


def _raw_name(tome: int) -> str:
    return f"tome_{tome:02d}.txt"


def _load_manifest(path: Path | None) -> Manifest:
    text = filesystem.read_packaged_manifest() if path is None else filesystem.read_text(path)
    try:
        return parse_manifest(json.loads(text))
    except (ManifestError, json.JSONDecodeError) as error:
        raise CliError(EXIT_CHECK_FAILED, f"invalid manifest: {error}") from error


def _download_all(manifest: Manifest) -> list[tuple[Source, bytes]]:
    return [(source, network.download(source.url)) for source in manifest.sources]


def _raise_on_checksum_problems(downloads: list[tuple[Source, bytes]]) -> None:
    problems = [problem for source, raw in downloads if (problem := source_problem(source, raw))]
    if problems:
        raise CliError(EXIT_CHECK_FAILED, "\n".join(problems) + "\nno file was written")


def _fetch(args: argparse.Namespace) -> int:
    downloads = _download_all(_load_manifest(args.manifest))
    _raise_on_checksum_problems(downloads)
    for written, (source, raw) in enumerate(downloads):
        try:
            filesystem.write_bytes_atomic(args.output_dir / _raw_name(source.tome), raw)
        except OSError as error:
            message = f"write failed after {written} of {len(downloads)} tomes: {error}"
            raise CliError(
                EXIT_ENVIRONMENT, message + "\nthe output directory may mix versions"
            ) from error
    print(f"fetched {len(downloads)} tomes into {args.output_dir}")
    return EXIT_OK


def _build(args: argparse.Namespace) -> int:
    manifest = _load_manifest(None)
    raws = []
    for source in manifest.sources:
        path = args.input_dir / _raw_name(source.tome)
        if not path.is_file():
            raise CliError(EXIT_ENVIRONMENT, f"missing raw tome: {path}")
        raws.append(filesystem.read_text(path))
    corpus = build_corpus(raws)
    data = corpus.encode("utf-8")  # pragma: no mutate
    filesystem.write_bytes_atomic(args.output, data)
    stats = describe(corpus)
    summary = {
        "sha256": sha256_hex(data),
        "characters": stats.characters,
        "lines": stats.lines,
        "vocabulary_size": stats.vocabulary_size,
    }
    print(json.dumps(summary, sort_keys=True))
    return EXIT_OK


def _verify(args: argparse.Namespace) -> int:
    manifest = _load_manifest(args.manifest)
    if not args.corpus.is_file():
        raise CliError(EXIT_ENVIRONMENT, f"corpus not found: {args.corpus}")
    problems = check_corpus(manifest, filesystem.read_text(args.corpus))
    if problems:
        raise CliError(EXIT_CHECK_FAILED, "verification failed:\n" + "\n".join(problems))
    print(f"verified {args.corpus}")
    return EXIT_OK


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tiny-corneille",
        description="Build a clean French text corpus from the Gutenberg tomes of Corneille's "
        "works.",
        epilog="exit codes: 0 ok, 1 check failed, 2 usage error, 3 environment error",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(required=True, metavar="COMMAND")

    fetch = commands.add_parser("fetch", help="download the raw tomes and check their checksums")
    fetch.add_argument("--manifest", type=Path, help="manifest file (default: packaged)")
    fetch.add_argument(
        "--output-dir", type=Path, default=DEFAULT_RAW_DIR, help="where to write the raw tomes"
    )
    fetch.set_defaults(handler=_fetch)

    build = commands.add_parser("build", help="clean the raw tomes into one corpus file")
    build.add_argument(
        "--input-dir", type=Path, default=DEFAULT_RAW_DIR, help="directory of raw tomes"
    )
    build.add_argument("--output", type=Path, default=DEFAULT_CORPUS, help="corpus file to write")
    build.set_defaults(handler=_build)

    verify = commands.add_parser("verify", help="check a corpus file against the manifest")
    verify.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS, help="corpus file to check")
    verify.add_argument("--manifest", type=Path, help="manifest file (default: packaged)")
    verify.set_defaults(handler=_verify)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return the exit code."""
    args = _build_parser().parse_args(argv)
    handler: Callable[[argparse.Namespace], int] = args.handler
    try:
        return handler(args)
    except CliError as error:
        print(f"error: {error.message}", file=sys.stderr)
        return error.code
    except network.DownloadError as error:
        print(f"error: download failed: {error}", file=sys.stderr)
        return EXIT_ENVIRONMENT
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_ENVIRONMENT
    except (UnicodeDecodeError, BoilerplateError) as error:
        print(f"error: invalid input: {error}", file=sys.stderr)
        return EXIT_CHECK_FAILED
