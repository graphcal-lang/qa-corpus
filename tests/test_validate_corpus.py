from __future__ import annotations

from pathlib import Path

import pytest

from qa_corpus import validate_repository


def create_repository(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "projects").mkdir(parents=True)
    return root


def write_inventory(root: Path, projects: str = "projects = []") -> None:
    (root / "corpus.toml").write_text(
        f"schema_version = 1\n\n{projects}\n", encoding="utf-8"
    )


def case_entry(
    identifier: str = "nominal-check",
    entry: str = "src/main.gcl",
    operation: str = "check",
) -> str:
    return (
        "[[projects.cases]]\n"
        f'id = "{identifier}"\n'
        f'entry = "{entry}"\n'
        f'operation = "{operation}"\n'
    )


def inventory_entry(
    identifier: str,
    path: str,
    cases: str | None = None,
    status: str = "active",
) -> str:
    return (
        "[[projects]]\n"
        f'id = "{identifier}"\n'
        f'path = "{path}"\n'
        f'status = "{status}"\n'
        f"{case_entry() if cases is None else cases}"
    )


def create_project(
    root: Path,
    path: str,
    entries: tuple[str, ...] = ("src/main.gcl",),
    *,
    graphcal_manifest: bool = True,
) -> None:
    project_root = root / path
    project_root.mkdir(parents=True)
    if graphcal_manifest:
        (project_root / "graphcal.toml").write_text("", encoding="utf-8")
    for entry in entries:
        entry_path = project_root / entry
        entry_path.parent.mkdir(parents=True, exist_ok=True)
        entry_path.write_text("", encoding="utf-8")


def test_accepts_empty_inventory(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    write_inventory(root)

    assert validate_repository(root) == []


def test_rejects_schema_type_coercion(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    (root / "corpus.toml").write_text(
        'schema_version = "1"\n\nprojects = []\n', encoding="utf-8"
    )

    errors = validate_repository(root)

    assert any("schema_version" in error for error in errors), errors


def test_rejects_project_field_type_coercion(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    (root / "corpus.toml").write_text(
        "schema_version = 1\n\n"
        "[[projects]]\n"
        "id = 1\n"
        'path = "projects/one"\n'
        'status = "quarantined"\n'
        "cases = []\n",
        encoding="utf-8",
    )

    errors = validate_repository(root)

    assert any(
        "projects.0.id" in error and "valid string" in error for error in errors
    ), errors


def test_rejects_unknown_root_fields(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    (root / "corpus.toml").write_text(
        "schema_version = 1\nunexpected = true\nprojects = []\n", encoding="utf-8"
    )

    errors = validate_repository(root)

    assert any(
        "unexpected" in error and "not permitted" in error for error in errors
    ), errors


def test_accepts_deferred_project_and_case_metadata(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    path = "projects/metadata"
    cases = case_entry() + 'expectation = "health-only"\n'
    project = inventory_entry("metadata", path, cases).replace(
        'status = "active"\n', 'status = "active"\ndomain = "systems"\n'
    )
    write_inventory(root, project)
    create_project(root, path)

    assert validate_repository(root) == []


def test_accepts_project_without_separate_qa_manifest(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    path = "projects/rocket-stage-sizing"
    write_inventory(root, inventory_entry("rocket-stage-sizing", path))
    create_project(root, path)

    assert validate_repository(root) == []


def test_accepts_multiple_case_entrypoints(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    path = "projects/power-budget"
    cases = case_entry("nominal-check", "src/nominal.gcl", "check") + case_entry(
        "contingency-eval", "src/contingency.gcl", "evaluate"
    )
    write_inventory(root, inventory_entry("power-budget", path, cases))
    create_project(root, path, ("src/nominal.gcl", "src/contingency.gcl"))

    assert validate_repository(root) == []


def test_accepts_quarantined_project_without_cases(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    path = "projects/generated-candidate"
    write_inventory(
        root,
        inventory_entry(
            "generated-candidate", path, "cases = []\n", status="quarantined"
        ),
    )
    create_project(root, path, entries=())

    assert validate_repository(root) == []


def test_rejects_active_project_without_cases(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    path = "projects/no-cases"
    write_inventory(root, inventory_entry("no-cases", path, "cases = []\n"))
    create_project(root, path, entries=())

    errors = validate_repository(root)

    assert any("at least one case while active" in error for error in errors), errors


def test_rejects_duplicate_project_ids(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    path = "projects/duplicate"
    write_inventory(
        root,
        inventory_entry("duplicate", path) + inventory_entry("duplicate", path),
    )
    create_project(root, path)

    errors = validate_repository(root)

    assert any("duplicate project id" in error for error in errors), errors


def test_rejects_duplicate_case_ids(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    path = "projects/thermal-balance"
    cases = case_entry("nominal", "src/first.gcl") + case_entry(
        "nominal", "src/second.gcl", "evaluate"
    )
    write_inventory(root, inventory_entry("thermal-balance", path, cases))
    create_project(root, path, ("src/first.gcl", "src/second.gcl"))

    errors = validate_repository(root)

    assert any("duplicate case id" in error for error in errors), errors


def test_rejects_traversal_path(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    write_inventory(root, inventory_entry("escape", "../outside"))

    errors = validate_repository(root)

    assert any("exactly the form" in error for error in errors), errors


def test_rejects_project_path_that_does_not_match_id(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    write_inventory(root, inventory_entry("power-budget", "projects/budget"))
    create_project(root, "projects/budget")

    errors = validate_repository(root)

    assert any("must end with its id" in error for error in errors), errors


def test_rejects_missing_graphcal_manifest(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    path = "projects/missing-manifest"
    write_inventory(root, inventory_entry("missing-manifest", path))
    create_project(root, path, graphcal_manifest=False)

    errors = validate_repository(root)

    assert any("Missing Graphcal project manifest" in error for error in errors), errors


def test_rejects_missing_case_entry_file(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    path = "projects/missing-entry"
    write_inventory(root, inventory_entry("missing-entry", path))
    create_project(root, path, entries=())

    errors = validate_repository(root)

    assert any("Case entry file is missing" in error for error in errors), errors


def test_rejects_case_entry_traversal(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    path = "projects/entry-escape"
    cases = case_entry(entry="../outside.gcl")
    write_inventory(root, inventory_entry("entry-escape", path, cases))
    create_project(root, path, entries=())

    errors = validate_repository(root)

    assert any(
        "projects.0.cases.0.entry" in error and "invalid component" in error
        for error in errors
    ), errors


def test_rejects_undeclared_project_directory(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    write_inventory(root)
    create_project(root, "projects/undeclared")

    errors = validate_repository(root)

    assert any("Undeclared project directory" in error for error in errors), errors


def test_rejects_symlinked_project_that_escapes_repository(tmp_path: Path) -> None:
    root = create_repository(tmp_path)
    path = "projects/external"
    write_inventory(root, inventory_entry("external", path))
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
