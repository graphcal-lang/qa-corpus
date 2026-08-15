from __future__ import annotations

from pathlib import Path

import pytest

from scripts.validate_corpus import validate_repository


def create_repository(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "projects").mkdir(parents=True)
    return root


def write_inventory(root: Path, projects: str = "projects = []") -> None:
    (root / "corpus.toml").write_text(
        f"schema_version = 1\n\n{projects}\n", encoding="utf-8"
    )


def create_project(
    root: Path,
    path: str,
    identifier: str,
    *,
    graphcal_manifest: bool = True,
    qa_manifest: bool = True,
) -> None:
    project_root = root / path
    project_root.mkdir(parents=True)
    if graphcal_manifest:
        (project_root / "graphcal.toml").write_text("", encoding="utf-8")
    if qa_manifest:
        (project_root / "qa.toml").write_text(
            f'schema_version = 1\n\n[project]\nid = "{identifier}"\n',
            encoding="utf-8",
        )


def inventory_entry(identifier: str, path: str) -> str:
    return f'[[projects]]\nid = "{identifier}"\npath = "{path}"\nstatus = "active"\n'


def test_accepts_empty_inventory(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    write_inventory(root)

    assert validate_repository(root) == []


def test_accepts_declared_project_with_both_manifests(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    path = "projects/propulsion/rocket-stage-sizing"
    write_inventory(root, inventory_entry("rocket-stage-sizing", path))
    create_project(root, path, "rocket-stage-sizing")

    assert validate_repository(root) == []


def test_rejects_duplicate_project_ids(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    first_path = "projects/propulsion/first"
    second_path = "projects/thermal/second"
    write_inventory(
        root,
        inventory_entry("duplicate", first_path)
        + inventory_entry("duplicate", second_path),
    )
    create_project(root, first_path, "duplicate")
    create_project(root, second_path, "duplicate")

    errors = validate_repository(root)

    assert any("Duplicate project id" in error for error in errors), errors


def test_rejects_traversal_path(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    write_inventory(root, inventory_entry("escape", "../outside"))

    errors = validate_repository(root)

    assert any("exactly the form" in error for error in errors), errors


def test_rejects_missing_project_manifests(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    path = "projects/thermal/missing-manifests"
    write_inventory(root, inventory_entry("missing-manifests", path))
    create_project(
        root,
        path,
        "missing-manifests",
        graphcal_manifest=False,
        qa_manifest=False,
    )

    errors = validate_repository(root)

    assert any("Missing Graphcal project manifest" in error for error in errors), errors
    assert any("Missing QA project manifest" in error for error in errors), errors


def test_rejects_undeclared_project_directory(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    write_inventory(root)
    create_project(root, "projects/thermal/undeclared", "undeclared")

    errors = validate_repository(root)

    assert any("Undeclared project directory" in error for error in errors), errors


def test_rejects_mismatched_qa_project_id(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    path = "projects/power/budget"
    write_inventory(root, inventory_entry("power-budget", path))
    create_project(root, path, "different-id")

    errors = validate_repository(root)

    assert any("project.id must match" in error for error in errors), errors


def test_rejects_symlinked_project_that_escapes_repository(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    path = "projects/thermal/external"
    write_inventory(root, inventory_entry("external", path))
    (root / "projects" / "thermal").mkdir()
    external_directory = tmp_path / "external"
    external_directory.mkdir()

    link = root / path
    try:
        link.symlink_to(external_directory, target_is_directory=True)
    except NotImplementedError, OSError:
        pytest.skip("symbolic links are unavailable")

    errors = validate_repository(root)

    assert any("Project path escapes the repository" in error for error in errors), (
        errors
    )
    assert any("Symbolic links are prohibited" in error for error in errors), errors


def test_rejects_symlinks_in_projects(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    write_inventory(root)
    target = root / "target.txt"
    target.write_text("public", encoding="utf-8")
    link = root / "projects" / "linked.txt"
    try:
        link.symlink_to(target)
    except NotImplementedError, OSError:
        pytest.skip("symbolic links are unavailable")

    errors = validate_repository(root)

    assert any("Symbolic links are prohibited" in error for error in errors), errors
