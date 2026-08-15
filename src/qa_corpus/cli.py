"""Command-line interface for structural corpus validation."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from qa_corpus.repository import validate_repository


def _parse_args(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate qa-corpus structure without executing project content."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root (default: current directory)",
    )
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    args = _parse_args(arguments)
    errors = validate_repository(args.root)
    if errors:
        print(f"Corpus structural validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Corpus structure is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
