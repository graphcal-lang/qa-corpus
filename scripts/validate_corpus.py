#!/usr/bin/env -S uv run
"""Validate the qa-corpus inventory without executing project content."""

from __future__ import annotations

import argparse
import os
import re
import sys
import tomllib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_VERSION = 1
ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
PROJECT_STATUSES = frozenset({"active", "quarantined"})


@dataclass(frozen=True)
class ProjectEntry:
    identifier: str
    path: str
    status: str


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


def _validate_schema_version(data: dict[str, Any], label: str) -> list[str]:
    version = data.get("schema_version")
    if type(version) is not int or version != SCHEMA_VERSION:
        return [
            f"{label} schema_version must be integer {SCHEMA_VERSION}, got {version!r}"
        ]
    return []


def _validate_project_path(raw_path: str) -> list[str]:
    path = PurePosixPath(raw_path)
    errors: list[str] = []

    if "\\" in raw_path:
        errors.append(f"Project path must use POSIX separators: {raw_path!r}")
    if path.is_absolute():
        errors.append(f"Project path must be relative: {raw_path!r}")
    if path.as_posix() != raw_path:
        errors.append(f"Project path must be canonical: {raw_path!r}")
    if len(path.parts) != 3 or not path.parts or path.parts[0] != "projects":
        errors.append(
            "Project path must have exactly the form "
            f"projects/<domain>/<project>: {raw_path!r}"
        )
    if any(part in {"", ".", ".."} for part in path.parts):
        errors.append(f"Project path contains an invalid component: {raw_path!r}")
    elif any(not ID_PATTERN.fullmatch(part) for part in path.parts[1:]):
        errors.append(
            f"Project path components must be lowercase kebab-case: {raw_path!r}"
        )

    return errors


def _parse_inventory(data: dict[str, Any]) -> tuple[list[ProjectEntry], list[str]]:
    errors = _validate_schema_version(data, "corpus.toml")
    raw_projects = data.get("projects")
    if not isinstance(raw_projects, list):
        return [], errors + ["corpus.toml projects must be an array of tables"]

    entries: list[ProjectEntry] = []
    for index, raw_entry in enumerate(raw_projects):
        label = f"corpus.toml projects[{index}]"
        if not isinstance(raw_entry, dict):
            errors.append(f"{label} must be a table")
            continue

        identifier = raw_entry.get("id")
        path = raw_entry.get("path")
        status = raw_entry.get("status")

        if not isinstance(identifier, str):
            errors.append(f"{label}.id must be a string")
        elif not ID_PATTERN.fullmatch(identifier):
            errors.append(f"{label}.id must be lowercase kebab-case: {identifier!r}")

        if not isinstance(path, str):
            errors.append(f"{label}.path must be a string")
        else:
            errors.extend(_validate_project_path(path))

        if not isinstance(status, str):
            errors.append(f"{label}.status must be a string")
        elif status not in PROJECT_STATUSES:
            allowed = ", ".join(sorted(PROJECT_STATUSES))
            errors.append(f"{label}.status must be one of {allowed}: {status!r}")

        if all(isinstance(value, str) for value in (identifier, path, status)):
            entries.append(ProjectEntry(identifier, path, status))

    duplicate_ids = sorted(
        identifier
        for identifier, count in Counter(entry.identifier for entry in entries).items()
        if count > 1
    )
    duplicate_paths = sorted(
        path
        for path, count in Counter(entry.path for entry in entries).items()
        if count > 1
    )
    errors.extend(
        f"Duplicate project id: {identifier!r}" for identifier in duplicate_ids
    )
    errors.extend(f"Duplicate project path: {path!r}" for path in duplicate_paths)

    return entries, errors


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
        for domain in projects_root.iterdir()
        if domain.is_dir() and not domain.is_symlink()
        for project in domain.iterdir()
        if project.is_dir() and not project.is_symlink()
    }


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _validate_qa_manifest(
    data: dict[str, Any], entry: ProjectEntry, manifest_path: Path
) -> list[str]:
    errors = _validate_schema_version(data, manifest_path.as_posix())
    project = data.get("project")
    if not isinstance(project, dict):
        return errors + [f"{manifest_path} must contain a [project] table"]

    identifier = project.get("id")
    if identifier != entry.identifier:
        errors.append(
            f"{manifest_path} project.id must match {entry.identifier!r}, "
            f"got {identifier!r}"
        )
    return errors


def _validate_declared_project(root: Path, entry: ProjectEntry) -> list[str]:
    path_errors = _validate_project_path(entry.path)
    if path_errors:
        return []

    project_root = (root / Path(*PurePosixPath(entry.path).parts)).resolve()
    if not _is_within(project_root, root):
        return [f"Project path escapes the repository: {entry.path!r}"]
    if not project_root.is_dir():
        return [f"Declared project directory is missing: {entry.path}"]

    errors: list[str] = []
    _, graphcal_errors = _load_toml(
        project_root / "graphcal.toml", "Graphcal project manifest"
    )
    errors.extend(graphcal_errors)

    qa_path = project_root / "qa.toml"
    qa_data, qa_errors = _load_toml(qa_path, "QA project manifest")
    errors.extend(qa_errors)
    if qa_data is not None:
        errors.extend(_validate_qa_manifest(qa_data, entry, qa_path))

    return errors


def validate_repository(root: Path) -> list[str]:
    """Return every structural validation error found under root."""
    root = root.resolve()
    corpus_data, errors = _load_toml(root / "corpus.toml", "corpus manifest")
    if corpus_data is None:
        return errors

    entries, inventory_errors = _parse_inventory(corpus_data)
    errors.extend(inventory_errors)

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

    valid_declared_paths = {
        entry.path for entry in entries if not _validate_project_path(entry.path)
    }
    discovered_paths = _discover_project_directories(projects_root)
    errors.extend(
        f"Undeclared project directory: {path}"
        for path in sorted(discovered_paths - valid_declared_paths)
    )

    for entry in entries:
        errors.extend(_validate_declared_project(root, entry))

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
