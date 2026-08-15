"""Typed, filesystem-independent corpus manifest validation."""

from __future__ import annotations

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


def _validate_case_entry_path(value: str) -> str:
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


StableId = Annotated[str, AfterValidator(_validate_stable_id)]
ProjectPath = Annotated[str, AfterValidator(_validate_project_path)]
CaseEntryPath = Annotated[str, AfterValidator(_validate_case_entry_path)]


class ProjectStatus(StrEnum):
    ACTIVE = "active"
    QUARANTINED = "quarantined"


class CaseOperation(StrEnum):
    CHECK = "check"
    EVALUATE = "evaluate"


class ExtensibleManifestModel(BaseModel):
    """Strict bootstrap fields with forward-compatible additional metadata."""

    model_config = ConfigDict(
        strict=True,
        extra="allow",
        frozen=True,
        hide_input_in_errors=True,
    )


class CaseEntry(ExtensibleManifestModel):
    id: StableId
    entry: CaseEntryPath
    operation: CaseOperation = Field(strict=False)


class ProjectEntry(ExtensibleManifestModel):
    id: StableId
    path: ProjectPath
    status: ProjectStatus = Field(strict=False)
    cases: list[CaseEntry]

    @model_validator(mode="after")
    def validate_project_invariants(self) -> Self:
        if self.path != f"projects/{self.id}":
            raise ValueError(f"project path must end with its id {self.id!r}")

        duplicate_case_ids = _duplicates(case.id for case in self.cases)
        if duplicate_case_ids:
            duplicates = ", ".join(repr(value) for value in duplicate_case_ids)
            raise ValueError(f"duplicate case id: {duplicates}")

        if self.status is ProjectStatus.ACTIVE and not self.cases:
            raise ValueError("must declare at least one case while active")

        return self


class CorpusManifest(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        hide_input_in_errors=True,
    )

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
