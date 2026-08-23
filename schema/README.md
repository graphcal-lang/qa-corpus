# Corpus manifest schema version 1

`corpus.toml` is the single machine-readable inventory of Graphcal projects, runnable cases, and their expectations. The structural validator parses it into strict Pydantic models before the runner opens any project data.

## Project inventory

```toml
schema_version = 1

[[projects]]
id = "rocket-stage-sizing"
path = "projects/rocket-stage-sizing"
status = "active"
domain = "propulsion"
origin = "source-backed"
purpose = "Evaluate a nominal launch-vehicle stage sizing analysis."

[[projects.cases]]
id = "nominal"
entry = "src/rocket_stage_sizing/main.gcl"
expectation = { kind = "health-only" }
```

### Project rules

- `schema_version` is the integer `1`.
- `projects` is an array of tables, or `[]` for an empty corpus.
- `id` is a repository-wide, stable lowercase kebab-case identifier.
- `path` is exactly `projects/<project-id>`, with a directory name matching `id`.
- `status` is `active` or `quarantined`.
- Project identifiers and paths are unique.
- Every listed project exists and contains a valid TOML `graphcal.toml`.
- Every direct child directory of `projects/` is listed, including quarantined candidates. Directories never become active by discovery.
- Every project declares `cases`. An active project has at least one case; a quarantined project may use `cases = []`.

The validator interprets the fields above strictly without scalar coercion. Additional project-level descriptive and provenance metadata is currently allowed. Unknown root, case, expectation, comparison, tolerance, and assertion fields are rejected.

## Cases

Each case has:

- `id`: lowercase kebab-case, unique within its project.
- `entry`: canonical POSIX path to an existing regular file inside the project, unique within that project.
- `expectation`: exactly one of the typed contracts below.

A case represents one entrypoint and runs the standard formatting, checking, and evaluation pipeline. Do not create separate cases for those stages. The obsolete `operation` field is rejected.

The canonical case identity is `<project-id>/<case-id>`. Manifest order determines execution and report order.

## Expectations

### Health-only

```toml
expectation = { kind = "health-only" }
```

The case passes when `graphcal format --check`, `graphcal check`, and JSON evaluation all succeed. It makes no numerical correctness or stability claim.

### Stability baseline

```toml
[projects.cases.expectation]
kind = "stability-baseline"
expected = "expected/nominal.json"
evidence = "reference/baseline.md"

[projects.cases.expectation.comparison]
mode = "semantic-json"
tolerances = []
```

A stability baseline requires:

- `expected`: a strict JSON file under `expected/`.
- `evidence`: a Markdown record under `reference/` containing producing revisions, inputs, comparison rules, and repeated-run determinism evidence.
- `comparison.mode`: currently `semantic-json`.
- `comparison.tolerances`: zero or more narrowly scoped numeric tolerances.

Semantic JSON comparison ignores object key order, preserves array order, rejects missing or additional values, and otherwise compares values exactly by JSON type and value. JSON integers and floats are both numbers. Duplicate object keys, non-finite values, and non-standard constants such as `NaN` are invalid.

An empty tolerance list makes every number exact. A tolerance applies only at one RFC 6901 JSON Pointer:

```toml
[[projects.cases.expectation.comparison.tolerances]]
pointer = "/node/delta_v/si_value"
absolute = 1e-9
relative = 1e-12
```

At least one bound is positive. Both bounds are non-negative and finite. The selected expected value must be numeric; duplicate tolerance pointers are rejected. A number passes when Python `math.isclose` accepts it with the declared bounds.

### Reference-backed

```toml
[projects.cases.expectation]
kind = "reference-backed"
evidence = "reference/calculation.md"

[[projects.cases.expectation.assertions]]
pointer = "/node/mass_ratio/si_value"
expected = 10.0
absolute_tolerance = 1.0
```

A reference-backed expectation requires:

- `evidence`: a Markdown calculation and provenance record under `reference/`.
- `assertions`: one or more unique JSON Pointer assertions against evaluated output.

`expected` is a JSON scalar representable in TOML: boolean, integer, float, or string. Numeric assertions use optional non-negative finite `absolute_tolerance` and `relative_tolerance` values, both zero by default. Non-numeric assertions are exact and cannot declare a positive tolerance.

The checked-in evidence must identify the source, assumptions, adaptations, conventions, independent calculation, and licensing status. The runner enforces the declared values but cannot establish that the evidence itself is trustworthy; human review remains required.

## Project files and paths

```text
projects/<project-id>/
├── graphcal.toml
├── src/
├── inputs/
├── expected/
└── reference/
```

Project, entry, expected, and evidence paths are relative canonical POSIX paths. Absolute paths, backslashes, `.` or `..` components, symbolic links, and any path resolving outside its allowed root are invalid. Expected paths must be `.json` files under `expected/`; evidence paths must be `.md` files under `reference/`.

The validator parses `graphcal.toml` and expected JSON but never invokes Graphcal or project-provided programs.

## Runner report

`test-graphcal` validates the repository, runs active cases, applies their expectations, and emits one versioned JSON report. Each case includes pipeline stage results and an expectation result:

```json
{
  "id": "ideal-rocket-equation/mass-ratio-ten",
  "status": "passed",
  "expectation": {
    "kind": "reference-backed",
    "status": "passed",
    "issues": []
  }
}
```

Expectation mismatches include their JSON Pointer and, when available, expected and actual values. A case and the overall command fail if any pipeline stage or expectation fails.

## Versioning

A schema version is a contract shared by this repository and consumers. Do not change version 1 incompatibly after adoption; add a new version and documented migration instead.
