#!/usr/bin/env -S uv run
"""Validate the qa-corpus inventory without executing project content."""

from __future__ import annotations

import argparse
import os
import re
import sys
import tomllib
from collections.abc import Iterable
from enum import StrEnum
from pathlib import Path, PurePosixPath
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


def _load_toml(path: Path, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    if path.is_symlink():
        return None, [f"{label} must not be a symbolic link: {path}"]

    try:
        with path.open("rb") as file:
            return tomllib.load(file), []
    except FileNotFoundError:
        return None, [f"Missing {label}: {path}"]
    except IsADirectoryError:
        return None, [f"Expected {label} to be a file: {path}"]
    except tomllib.TOMLDecodeError as error:
        return None, [f"Malformed {label} at {path}: {error}"]
    except OSError as error:
        return None, [f"Cannot read {label} at {path}: {error}"]


def _format_validation_error(error: ValidationError) -> list[str]:
    def format_issue(issue: dict[str, Any]) -> str:
        location = ".".join(str(part) for part in issue["loc"])
        label = f"corpus.toml {location}" if location else "corpus.toml"
        return f"{label}: {issue['msg']}"

    return [format_issue(issue) for issue in error.errors(include_url=False)]


def _parse_inventory(
    data: dict[str, Any],
) -> tuple[CorpusManifest | None, list[str]]:
    try:
        return CorpusManifest.model_validate(data), []
    except ValidationError as error:
        return None, _format_validation_error(error)


def _find_symlinks(projects_root: Path) -> list[Path]:
    if not projects_root.is_dir():
        return []

    symlinks: list[Path] = []
    for current_root, directory_names, file_names in os.walk(
        projects_root, followlinks=False
    ):
        current = Path(current_root)
        symlinks.extend(
            path
            for name in (*directory_names, *file_names)
            if (path := current / name).is_symlink()
        )
    return sorted(symlinks)


def _discover_project_directories(projects_root: Path) -> set[str]:
    if not projects_root.is_dir():
        return set()

    return {
        project.relative_to(projects_root.parent).as_posix()
        for project in projects_root.iterdir()
        if project.is_dir() and not project.is_symlink()
    }


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _validate_declared_project(root: Path, project: ProjectEntry) -> list[str]:
    project_root = (root / Path(*PurePosixPath(project.path).parts)).resolve()
    if not _is_within(project_root, root):
        return [f"Project path escapes the repository: {project.path!r}"]
    if not project_root.is_dir():
        return [f"Declared project directory is missing: {project.path}"]

    errors: list[str] = []
    _, graphcal_errors = _load_toml(
        project_root / "graphcal.toml", "Graphcal project manifest"
    )
    errors.extend(graphcal_errors)

    for case in project.cases:
        case_path = (project_root / Path(*PurePosixPath(case.entry).parts)).resolve()
        case_label = f"{project.id}/{case.id}"
        if not _is_within(case_path, project_root):
            errors.append(
                f"Case entry escapes its project for {case_label}: {case.entry!r}"
            )
        elif not case_path.is_file():
            errors.append(f"Case entry file is missing for {case_label}: {case.entry}")

    return errors


def validate_repository(root: Path) -> list[str]:
    """Return every structural validation error found under root."""
    root = root.resolve()
    corpus_data, errors = _load_toml(root / "corpus.toml", "corpus manifest")
    if corpus_data is None:
        return errors

    manifest, inventory_errors = _parse_inventory(corpus_data)
    errors.extend(inventory_errors)
    if manifest is None:
        return errors

    projects_root = root / "projects"
    if projects_root.is_symlink():
        errors.append(
            f"Projects directory must not be a symbolic link: {projects_root}"
        )
        return errors
    if not projects_root.is_dir():
        errors.append(f"Missing projects directory: {projects_root}")
        return errors

    errors.extend(
        f"Symbolic links are prohibited under projects/: "
        f"{path.relative_to(root).as_posix()}"
        for path in _find_symlinks(projects_root)
    )

    declared_paths = {project.path for project in manifest.projects}
    discovered_paths = _discover_project_directories(projects_root)
    errors.extend(
        f"Undeclared project directory: {path}"
        for path in sorted(discovered_paths - declared_paths)
    )

    for project in manifest.projects:
        errors.extend(_validate_declared_project(root, project))

    return errors


def _parse_args() -> argparse.Namespace:
    default_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Validate qa-corpus structure without executing project content."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help=f"repository root (default: {default_root})",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    errors = validate_repository(args.root)
    if errors:
        print(f"Corpus structural validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1

    corpus_data, _ = _load_toml(args.root.resolve() / "corpus.toml", "corpus manifest")
    project_count = len(corpus_data.get("projects", [])) if corpus_data else 0
    print(f"Corpus structure is valid ({project_count} declared projects).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
