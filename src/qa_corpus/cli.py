"""Typer command-line interface for structural corpus validation."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from qa_corpus.repository import validate_repository

app = typer.Typer(add_completion=False)


@app.command()
def main(
    root: Annotated[
        Path,
        typer.Option(
            help="Repository root.",
            metavar="PATH",
        ),
    ] = Path("."),
) -> None:
    """Validate qa-corpus structure without executing project content."""
    errors = validate_repository(root)
    if errors:
        typer.echo(f"Corpus structural validation failed with {len(errors)} error(s):")
        for error in errors:
            typer.echo(f"- {error}")
        raise typer.Exit(code=1)

    typer.echo("Corpus structure is valid.")


if __name__ == "__main__":
    app()
