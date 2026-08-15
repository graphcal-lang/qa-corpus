"""Run active corpus cases with a caller-supplied Graphcal executable."""

from __future__ import annotations

import json
import math
import subprocess
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal

from qa_corpus.manifest import CorpusManifest, ProjectStatus

StageStatus = Literal["passed", "failed", "skipped"]


@dataclass(frozen=True)
class CasePlan:
    """A validated active case and its execution directory."""

    project_id: str
    case_id: str
    project_root: Path
    entry: str


@dataclass(frozen=True)
class StageResult:
    """Captured outcome of one Graphcal subprocess."""

    status: StageStatus
    exit_code: int | None
    stdout: str
    stderr: str
    error: str | None = None
    result: Any = None
    has_result: bool = False

    def to_json(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "status": self.status,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }
        if self.error is not None:
            value["error"] = self.error
        if self.has_result:
            value["result"] = self.result
        return value


def plan_active_cases(root: Path, manifest: CorpusManifest) -> tuple[CasePlan, ...]:
    """Create deterministic execution plans from a validated manifest."""
    return tuple(
        CasePlan(
            project_id=project.id,
            case_id=case.id,
            project_root=root / project.path,
            entry=case.entry,
        )
        for project in manifest.projects
        if project.status is ProjectStatus.ACTIVE
        for case in project.cases
    )


def _text(value: str | bytes | None) -> str:
    match value:
        case None:
            return ""
        case bytes():
            return value.decode("utf-8", errors="replace")
        case str():
            return value


def _run_stage(command: list[str], cwd: Path, timeout: float) -> StageResult:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        return StageResult(
            status="failed",
            exit_code=None,
            stdout=_text(error.stdout),
            stderr=_text(error.stderr),
            error=f"timed out after {timeout:g} seconds",
        )
    except OSError as error:
        return StageResult(
            status="failed",
            exit_code=None,
            stdout="",
            stderr="",
            error=f"could not execute Graphcal: {error}",
        )

    return StageResult(
        status="passed" if completed.returncode == 0 else "failed",
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _reject_nonstandard_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value!r}")


def _parse_finite_json_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"JSON number is outside the finite float range: {value}")
    return parsed


def _parse_evaluation_result(stage: StageResult) -> StageResult:
    if stage.status != "passed":
        return stage

    try:
        result = json.loads(
            stage.stdout,
            parse_constant=_reject_nonstandard_json_constant,
            parse_float=_parse_finite_json_float,
        )
    except (json.JSONDecodeError, ValueError) as error:
        return replace(
            stage,
            status="failed",
            error=f"evaluation stdout is not valid JSON: {error}",
        )

    return replace(stage, result=result, has_result=True)


def _skipped_stage(reason: str) -> StageResult:
    return StageResult(
        status="skipped",
        exit_code=None,
        stdout="",
        stderr="",
        error=reason,
    )


def _run_case(
    executable: Path,
    plan: CasePlan,
    timeout: float,
) -> dict[str, Any]:
    formatting = _run_stage(
        [str(executable), "format", "--check", plan.entry],
        cwd=plan.project_root,
        timeout=timeout,
    )
    check = _run_stage(
        [str(executable), "check", "--root", ".", plan.entry],
        cwd=plan.project_root,
        timeout=timeout,
    )

    if check.status == "passed":
        evaluation = _parse_evaluation_result(
            _run_stage(
                [
                    str(executable),
                    "eval",
                    "--format",
                    "json",
                    "--root",
                    ".",
                    plan.entry,
                ],
                cwd=plan.project_root,
                timeout=timeout,
            )
        )
    else:
        evaluation = _skipped_stage("not run because checking failed")

    status = (
        "passed"
        if formatting.status == "passed"
        and check.status == "passed"
        and evaluation.status == "passed"
        else "failed"
    )
    return {
        "id": f"{plan.project_id}/{plan.case_id}",
        "project_id": plan.project_id,
        "case_id": plan.case_id,
        "entry": plan.entry,
        "status": status,
        "stages": {
            "format": formatting.to_json(),
            "check": check.to_json(),
            "eval": evaluation.to_json(),
        },
    }


def error_report(executable: str, errors: list[str]) -> dict[str, Any]:
    """Build a JSON report for failures that prevent case execution."""
    return {
        "report_version": 1,
        "status": "failed",
        "executable": executable,
        "summary": {"total": 0, "passed": 0, "failed": 0},
        "cases": [],
        "errors": errors,
    }


def run_graphcal_cases(
    root: Path,
    executable: Path,
    manifest: CorpusManifest,
    *,
    timeout: float,
) -> dict[str, Any]:
    """Run all active cases and return a JSON-serializable report."""
    cases = [
        _run_case(executable, plan, timeout)
        for plan in plan_active_cases(root.resolve(), manifest)
    ]
    passed = sum(case["status"] == "passed" for case in cases)
    failed = len(cases) - passed
    return {
        "report_version": 1,
        "status": "passed" if failed == 0 else "failed",
        "executable": str(executable),
        "summary": {"total": len(cases), "passed": passed, "failed": failed},
        "cases": cases,
        "errors": [],
    }
