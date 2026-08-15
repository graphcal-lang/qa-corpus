"""Command-line interface for running corpus cases with Graphcal."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from collections.abc import Sequence
from pathlib import Path

from qa_corpus.repository import load_repository_manifest
from qa_corpus.runner import error_report, run_graphcal_cases


def _positive_timeout(value: str) -> float:
    try:
        timeout = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a number") from error
    if not math.isfinite(timeout) or timeout <= 0:
        raise argparse.ArgumentTypeError("must be a positive finite number")
    return timeout


def _parse_args(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run every active corpus case with a Graphcal executable and write "
            "one JSON report to stdout."
        )
    )
    parser.add_argument(
        "executable",
        help="Graphcal executable path or command name",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root (default: current directory)",
    )
    parser.add_argument(
        "--timeout",
        type=_positive_timeout,
        default=30.0,
        metavar="SECONDS",
        help="timeout for each format, check, or eval process (default: 30)",
    )
    return parser.parse_args(arguments)


def _resolve_executable(value: str) -> tuple[Path | None, str | None]:
    resolved = shutil.which(value)
    if resolved is None:
        return None, f"Graphcal executable was not found or is not executable: {value}"
    return Path(resolved).resolve(), None


def _write_report(report: dict[str, object]) -> None:
    json.dump(report, sys.stdout, indent=2, allow_nan=False)
    sys.stdout.write("\n")


def main(arguments: Sequence[str] | None = None) -> int:
    args = _parse_args(arguments)
    root = args.root.resolve()
    manifest, repository_errors = load_repository_manifest(root)
    executable, executable_error = _resolve_executable(args.executable)

    errors = [*repository_errors]
    if executable_error is not None:
        errors.append(executable_error)
    if manifest is None or executable is None or errors:
        _write_report(error_report(args.executable, errors))
        return 1

    report = run_graphcal_cases(
        root,
        executable,
        manifest,
        timeout=args.timeout,
    )
    _write_report(report)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
