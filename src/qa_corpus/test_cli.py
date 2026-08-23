"""Typer command-line interface for running corpus cases with Graphcal."""

from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path
from typing import Annotated, Any

import typer

from qa_corpus.repository import load_repository_manifest
from qa_corpus.runner import error_report, run_graphcal_cases

app = typer.Typer(add_completion=False)


def _positive_timeout(value: float) -> float:
    if not math.isfinite(value) or value <= 0:
        raise typer.BadParameter("must be a positive finite number")
    return value


def _resolve_executable(value: str) -> tuple[Path | None, str | None]:
    resolved = shutil.which(value)
    if resolved is None:
        return None, f"Graphcal executable was not found or is not executable: {value}"
    return Path(resolved).resolve(), None


def _write_report(report: dict[str, Any]) -> None:
    json.dump(report, sys.stdout, indent=2, allow_nan=False)
    sys.stdout.write("\n")


@app.command()
def main(
    executable_name: Annotated[
        str,
        typer.Argument(
            metavar="EXECUTABLE",
            help="Graphcal executable path or command name.",
        ),
    ],
    root: Annotated[
        Path,
        typer.Option(
            help="Repository root.",
            metavar="PATH",
        ),
    ] = Path("."),
    timeout: Annotated[
        float,
        typer.Option(
            callback=_positive_timeout,
            help="Timeout for each format, check, or eval process.",
            metavar="SECONDS",
        ),
    ] = 30.0,
) -> None:
    """Run every active corpus case and write one JSON report to stdout."""
    root = root.resolve()
    manifest, repository_errors = load_repository_manifest(root)
    executable, executable_error = _resolve_executable(executable_name)

    errors = [*repository_errors]
    if executable_error is not None:
        errors.append(executable_error)
    if manifest is None or executable is None or errors:
        _write_report(error_report(executable_name, errors))
        raise typer.Exit(code=1)

    report = run_graphcal_cases(
        root,
        executable,
        manifest,
        timeout=timeout,
    )
    _write_report(report)
    if report["status"] != "passed":
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
