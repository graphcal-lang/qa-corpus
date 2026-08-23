"""Typed, filesystem-independent corpus manifest validation."""

from __future__ import annotations

import math
import re
from collections.abc import Iterable
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    model_validator,
)

ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
INVALID_JSON_POINTER_ESCAPE = re.compile(r"~(?![01])")


def _validate_stable_id(value: str) -> str:
    if not ID_PATTERN.fullmatch(value):
        raise ValueError("must be lowercase kebab-case")
    return value


def _validate_project_path(value: str) -> str:
    path = PurePosixPath(value)
    if "\\" in value:
        raise ValueError("must use POSIX separators")
    if path.is_absolute():
        raise ValueError("must be relative")
    if path.as_posix() != value:
        raise ValueError("must be canonical")
    if len(path.parts) != 2 or not path.parts or path.parts[0] != "projects":
        raise ValueError("must have exactly the form projects/<project-id>")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("contains an invalid component")
    if not ID_PATTERN.fullmatch(path.parts[1]):
        raise ValueError("project directory must be lowercase kebab-case")
    return value


def _validate_relative_project_path(value: str) -> str:
    path = PurePosixPath(value)
    if "\\" in value:
        raise ValueError("must use POSIX separators")
    if path.is_absolute():
        raise ValueError("must be relative")
    if path.as_posix() != value:
        raise ValueError("must be canonical")
    if not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("contains an invalid component")
    return value


def _validate_expected_path(value: str) -> str:
    path = PurePosixPath(_validate_relative_project_path(value))
    if path.parts[0] != "expected" or path.suffix != ".json":
        raise ValueError("must be a JSON file under expected/")
    return value


def _validate_evidence_path(value: str) -> str:
    path = PurePosixPath(_validate_relative_project_path(value))
    if path.parts[0] != "reference" or path.suffix != ".md":
        raise ValueError("must be a Markdown file under reference/")
    return value


def _validate_json_pointer(value: str) -> str:
    if value and not value.startswith("/"):
        raise ValueError("must be empty or start with '/'")
    if INVALID_JSON_POINTER_ESCAPE.search(value):
        raise ValueError("contains an invalid '~' escape")
    return value


StableId = Annotated[str, AfterValidator(_validate_stable_id)]
ProjectPath = Annotated[str, AfterValidator(_validate_project_path)]
CaseEntryPath = Annotated[str, AfterValidator(_validate_relative_project_path)]
ExpectedPath = Annotated[str, AfterValidator(_validate_expected_path)]
EvidencePath = Annotated[str, AfterValidator(_validate_evidence_path)]
JsonPointer = Annotated[str, AfterValidator(_validate_json_pointer)]
FiniteNonnegativeFloat = Annotated[
    float,
    Field(ge=0.0, allow_inf_nan=False),
]
JsonScalar = bool | int | float | str


class ProjectStatus(StrEnum):
    ACTIVE = "active"
    QUARANTINED = "quarantined"


class StrictManifestModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        hide_input_in_errors=True,
    )


class ExtensibleProjectModel(BaseModel):
    """Strict core project fields with forward-compatible descriptive metadata."""

    model_config = ConfigDict(
        strict=True,
        extra="allow",
        frozen=True,
        hide_input_in_errors=True,
    )


class NumericTolerance(StrictManifestModel):
    pointer: JsonPointer
    absolute: FiniteNonnegativeFloat = 0.0
    relative: FiniteNonnegativeFloat = 0.0

    @model_validator(mode="after")
    def require_nonzero_tolerance(self) -> Self:
        if self.absolute == 0.0 and self.relative == 0.0:
            raise ValueError("must set a positive absolute or relative tolerance")
        return self


class SemanticJsonComparison(StrictManifestModel):
    mode: Literal["semantic-json"]
    tolerances: list[NumericTolerance] = Field(default_factory=list)

    @model_validator(mode="after")
    def reject_duplicate_tolerances(self) -> Self:
        duplicates = _duplicates(item.pointer for item in self.tolerances)
        if duplicates:
            raise ValueError(
                "; ".join(
                    f"duplicate numeric tolerance pointer: {pointer!r}"
                    for pointer in duplicates
                )
            )
        return self


class HealthOnlyExpectation(StrictManifestModel):
    kind: Literal["health-only"]


class StabilityBaselineExpectation(StrictManifestModel):
    kind: Literal["stability-baseline"]
    expected: ExpectedPath
    evidence: EvidencePath
    comparison: SemanticJsonComparison


class ValueAssertion(StrictManifestModel):
    pointer: JsonPointer
    expected: JsonScalar
    absolute_tolerance: FiniteNonnegativeFloat = 0.0
    relative_tolerance: FiniteNonnegativeFloat = 0.0

    @model_validator(mode="after")
    def validate_tolerance_kind(self) -> Self:
        if isinstance(self.expected, float) and not math.isfinite(self.expected):
            raise ValueError("expected number must be finite")
        has_tolerance = self.absolute_tolerance > 0.0 or self.relative_tolerance > 0.0
        if has_tolerance and isinstance(self.expected, (bool, str)):
            raise ValueError("tolerances require a numeric expected value")
        return self


class ReferenceBackedExpectation(StrictManifestModel):
    kind: Literal["reference-backed"]
    evidence: EvidencePath
    assertions: list[ValueAssertion]

    @model_validator(mode="after")
    def validate_assertions(self) -> Self:
        if not self.assertions:
            raise ValueError("must declare at least one assertion")
        duplicates = _duplicates(assertion.pointer for assertion in self.assertions)
        if duplicates:
            raise ValueError(
                "; ".join(
                    f"duplicate assertion pointer: {pointer!r}"
                    for pointer in duplicates
                )
            )
        return self


Expectation = Annotated[
    HealthOnlyExpectation | StabilityBaselineExpectation | ReferenceBackedExpectation,
    Field(discriminator="kind"),
]


class CaseEntry(StrictManifestModel):
    id: StableId
    entry: CaseEntryPath
    expectation: Expectation

    @model_validator(mode="before")
    @classmethod
    def reject_operation(cls, value: Any) -> Any:
        if isinstance(value, dict) and "operation" in value:
            raise ValueError(
                "operation is not supported; each case runs the standard entrypoint pipeline"
            )
        return value


class ProjectEntry(ExtensibleProjectModel):
    id: StableId
    path: ProjectPath
    status: ProjectStatus = Field(strict=False)
    cases: list[CaseEntry]

    @model_validator(mode="after")
    def validate_project_invariants(self) -> Self:
        if self.path != f"projects/{self.id}":
            raise ValueError(f"project path must end with its id {self.id!r}")

        duplicate_case_ids = _duplicates(case.id for case in self.cases)
        duplicate_case_entries = _duplicates(case.entry for case in self.cases)
        errors = [
            *(f"duplicate case id: {value!r}" for value in duplicate_case_ids),
            *(
                f"duplicate case entrypoint: {value!r}"
                for value in duplicate_case_entries
            ),
        ]
        if errors:
            raise ValueError("; ".join(errors))

        if self.status is ProjectStatus.ACTIVE and not self.cases:
            raise ValueError("must declare at least one case while active")

        return self


class CorpusManifest(StrictManifestModel):
    schema_version: Literal[1]
    projects: list[ProjectEntry]

    @model_validator(mode="after")
    def validate_inventory_uniqueness(self) -> Self:
        duplicate_ids = _duplicates(project.id for project in self.projects)
        duplicate_paths = _duplicates(project.path for project in self.projects)
        errors = [
            *(f"duplicate project id: {value!r}" for value in duplicate_ids),
            *(f"duplicate project path: {value!r}" for value in duplicate_paths),
        ]
        if errors:
            raise ValueError("; ".join(errors))
        return self


def _duplicates(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)
    return sorted(duplicates)


def _format_validation_error(error: ValidationError) -> list[str]:
    def format_issue(issue: dict[str, Any]) -> str:
        location = ".".join(str(part) for part in issue["loc"])
        label = f"corpus.toml {location}" if location else "corpus.toml"
        return f"{label}: {issue['msg']}"

    return [format_issue(issue) for issue in error.errors(include_url=False)]


def parse_manifest(
    data: dict[str, Any],
) -> tuple[CorpusManifest | None, list[str]]:
    """Parse untrusted TOML data into a typed corpus manifest."""
    try:
        return CorpusManifest.model_validate(data), []
    except ValidationError as error:
        return None, _format_validation_error(error)
