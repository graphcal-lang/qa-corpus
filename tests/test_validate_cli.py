from pathlib import Path

from typer.testing import CliRunner

from qa_corpus.cli import app

runner = CliRunner()


def test_reports_valid_repository(tmp_path: Path) -> None:
    (tmp_path / "projects").mkdir()
    (tmp_path / "corpus.toml").write_text(
        "schema_version = 1\nprojects = []\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["--root", str(tmp_path)])

    assert result.exit_code == 0
    assert result.stdout == "Corpus structure is valid.\n"
    assert result.stderr == ""


def test_reports_validation_errors(tmp_path: Path) -> None:
    result = runner.invoke(app, ["--root", str(tmp_path)])

    assert result.exit_code == 1
    assert "Corpus structural validation failed" in result.stdout
    assert "Missing corpus manifest" in result.stdout
    assert result.stderr == ""
