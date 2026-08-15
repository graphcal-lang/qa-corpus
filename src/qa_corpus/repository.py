"""Filesystem validation for a typed corpus manifest."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

from qa_corpus.manifest import CorpusManifest, ProjectEntry, parse_manifest


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


def load_repository_manifest(
    root: Path,
) -> tuple[CorpusManifest | None, list[str]]:
    """Load the manifest and return every structural validation error."""
    root = root.resolve()
    corpus_data, errors = _load_toml(root / "corpus.toml", "corpus manifest")
    if corpus_data is None:
        return None, errors

    manifest, inventory_errors = parse_manifest(corpus_data)
    errors.extend(inventory_errors)
    if manifest is None:
        return None, errors

    projects_root = root / "projects"
    if projects_root.is_symlink():
        errors.append(
            f"Projects directory must not be a symbolic link: {projects_root}"
        )
        return manifest, errors
    if not projects_root.is_dir():
        errors.append(f"Missing projects directory: {projects_root}")
        return manifest, errors

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

    return manifest, errors


def validate_repository(root: Path) -> list[str]:
    """Return every structural validation error found under root."""
    _, errors = load_repository_manifest(root)
    return errors
