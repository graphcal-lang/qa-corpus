from __future__ import annotations

import json
import stat
from pathlib import Path

from qa_corpus.test_cli import main


def create_project(root: Path, identifier: str, *, entry: str | None) -> None:
    project = root / "projects" / identifier
    project.mkdir(parents=True)
    (project / "graphcal.toml").write_text(
        f'[package]\nname = "{identifier.replace("-", "_")}"\n',
        encoding="utf-8",
    )
    if entry is not None:
        entry_path = project / entry
        entry_path.parent.mkdir(parents=True)
        entry_path.write_text("node answer = 42;\n", encoding="utf-8")


def create_repository(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    create_project(root, "active-project", entry="src/main.gcl")
    create_project(root, "quarantined-project", entry=None)
    (root / "corpus.toml").write_text(
        "schema_version = 1\n\n"
        "[[projects]]\n"
        'id = "active-project"\n'
        'path = "projects/active-project"\n'
        'status = "active"\n'
        "[[projects.cases]]\n"
        'id = "nominal"\n'
        'entry = "src/main.gcl"\n\n'
        "[[projects]]\n"
        'id = "quarantined-project"\n'
        'path = "projects/quarantined-project"\n'
        'status = "quarantined"\n'
        "cases = []\n",
        encoding="utf-8",
    )
    return root


def create_executable(tmp_path: Path, body: str) -> Path:
    executable = tmp_path / "fake-graphcal"
    executable.write_text(f"#!/bin/sh\nset -eu\n{body}\n", encoding="utf-8")
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    return executable


def read_report(capsys) -> dict[str, object]:
    captured = capsys.readouterr()
    assert captured.err == ""
    return json.loads(captured.out)


def test_runs_standard_pipeline_for_active_cases(tmp_path: Path, capsys) -> None:
    root = create_repository(tmp_path)
    executable = create_executable(
        tmp_path,
        """
case "$1" in
  format)
    test "$2" = "--check"
    test "$3" = "src/main.gcl"
    test -f graphcal.toml
    ;;
  check)
    test "$2" = "--root"
    test "$3" = "."
    test "$4" = "src/main.gcl"
    test -f graphcal.toml
    printf 'ok: %s\\n' "$4"
    ;;
  eval)
    test "$2" = "--format"
    test "$3" = "json"
    test "$4" = "--root"
    test "$5" = "."
    test "$6" = "src/main.gcl"
    test -f graphcal.toml
    printf '{"node":{"answer":42}}\\n'
    ;;
  *) exit 64 ;;
esac
""",
    )

    exit_code = main([str(executable), "--root", str(root)])
    report = read_report(capsys)

    assert exit_code == 0
    assert report["status"] == "passed"
    assert report["summary"] == {"total": 1, "passed": 1, "failed": 0}
    case = report["cases"][0]
    assert case["id"] == "active-project/nominal"
    assert case["stages"]["format"]["status"] == "passed"
    assert case["stages"]["check"]["status"] == "passed"
    assert case["stages"]["eval"]["result"] == {"node": {"answer": 42}}


def test_skips_eval_when_check_fails(tmp_path: Path, capsys) -> None:
    root = create_repository(tmp_path)
    executable = create_executable(
        tmp_path,
        """
case "$1" in
  format) exit 0 ;;
  check) printf 'type error\\n' >&2; exit 7 ;;
  eval) printf 'eval must not run\\n' >&2; exit 99 ;;
  *) exit 64 ;;
esac
""",
    )

    exit_code = main([str(executable), "--root", str(root)])
    report = read_report(capsys)

    assert exit_code == 1
    assert report["summary"] == {"total": 1, "passed": 0, "failed": 1}
    stages = report["cases"][0]["stages"]
    assert stages["check"]["exit_code"] == 7
    assert stages["check"]["stderr"] == "type error\n"
    assert stages["eval"]["status"] == "skipped"


def test_fails_case_when_formatting_fails_but_runs_other_stages(
    tmp_path: Path, capsys
) -> None:
    root = create_repository(tmp_path)
    executable = create_executable(
        tmp_path,
        """
case "$1" in
  format) printf 'needs formatting\\n'; exit 1 ;;
  check) exit 0 ;;
  eval) printf 'null\\n'; exit 0 ;;
  *) exit 64 ;;
esac
""",
    )

    exit_code = main([str(executable), "--root", str(root)])
    report = read_report(capsys)

    assert exit_code == 1
    stages = report["cases"][0]["stages"]
    assert stages["format"]["status"] == "failed"
    assert stages["check"]["status"] == "passed"
    assert stages["eval"]["status"] == "passed"
    assert "result" in stages["eval"]
    assert stages["eval"]["result"] is None


def test_rejects_non_json_eval_stdout(tmp_path: Path, capsys) -> None:
    root = create_repository(tmp_path)
    executable = create_executable(
        tmp_path,
        """
case "$1" in
  format) exit 0 ;;
  check) exit 0 ;;
  eval) printf 'not json\\n'; exit 0 ;;
  *) exit 64 ;;
esac
""",
    )

    exit_code = main([str(executable), "--root", str(root)])
    report = read_report(capsys)

    assert exit_code == 1
    evaluation = report["cases"][0]["stages"]["eval"]
    assert evaluation["status"] == "failed"
    assert "not valid JSON" in evaluation["error"]


def test_reports_structural_errors_as_json_without_execution(
    tmp_path: Path, capsys
) -> None:
    root = tmp_path / "invalid-repo"
    root.mkdir()
    (root / "corpus.toml").write_text(
        "schema_version = 1\nprojects = []\n", encoding="utf-8"
    )
    marker = tmp_path / "executed"
    executable = create_executable(tmp_path, f"touch '{marker}'")

    exit_code = main([str(executable), "--root", str(root)])
    report = read_report(capsys)

    assert exit_code == 1
    assert report["status"] == "failed"
    assert report["cases"] == []
    assert any("Missing projects directory" in error for error in report["errors"])
    assert not marker.exists()


def test_reports_missing_executable_as_json(tmp_path: Path, capsys) -> None:
    root = create_repository(tmp_path)

    exit_code = main(["definitely-not-a-graphcal-command", "--root", str(root)])
    report = read_report(capsys)

    assert exit_code == 1
    assert report["cases"] == []
    assert "was not found" in report["errors"][0]
