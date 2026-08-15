# Bootstrap manifest schema

This document defines schema version 1 for structural validation. `corpus.toml` is the single machine-readable source for the project inventory and QA cases. The trusted Graphcal runner will extend the typed case and assertion contract in a later phase; fields not needed for bootstrap validation are intentionally deferred.

## `corpus.toml`

A project and two cases with different entrypoints are represented as:

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
id = "nominal-check"
entry = "src/nominal.gcl"
operation = "check"

[[projects.cases]]
id = "contingency-eval"
entry = "src/contingency.gcl"
operation = "evaluate"
```

The bootstrap validator requires and interprets `schema_version`, each project's `id`, `path`, `status`, and `cases`, and each case's `id`, `entry`, and `operation`. Descriptive, provenance, expectation, assertion, comparison-profile, and timeout fields also belong in `corpus.toml`, but their typed representation will be finalized with the trusted runner. Large expected outputs and reference calculations remain files inside the project and are referenced by relative path.

### Project rules

- `schema_version` must be the integer `1`.
- `projects` must be an array of tables (or `[]` for an empty corpus).
- `id` is a repository-wide, stable lowercase kebab-case identifier.
- `path` is exactly `projects/<project-id>`, and the directory name must match `id`.
- `status` is `active` or `quarantined`.
- Project identifiers and paths must be unique.
- Every listed path must exist and contain a valid TOML `graphcal.toml`.
- Every direct child directory of `projects/` must be listed, even when quarantined. Directories never become active by discovery.
- Every project must declare a `cases` array. An active project must contain at least one case; a quarantined project may use `cases = []`.

To add the first project, remove the root `projects = []` before adding `[[projects]]` tables.

### Case rules

- `id` is stable lowercase kebab-case and unique within its project. The canonical corpus identity is the project ID plus case ID.
- `entry` is a canonical POSIX path relative to the project directory. It must resolve to an existing regular file inside that project.
- `operation` is `check` or `evaluate`.
- Each case independently declares its entry file, so one project may exercise multiple entrypoints. Cases may also share an entry when they exercise different operations or inputs.

Absolute paths, `.` or `..` components, backslashes, symbolic links, and any project or case path resolving outside its allowed root are invalid.

## Project directories

A project directory contains Graphcal data and supporting evidence, not a second QA manifest:

```text
projects/<project-id>/
├── graphcal.toml
├── src/
├── inputs/
├── expected/
└── reference/
```

The validator parses `graphcal.toml` as TOML but does not interpret it and never invokes Graphcal or project-provided programs.

## Versioning

A schema version denotes a contract shared with the Graphcal-side runner. Do not change the meaning of version 1 in place after that runner adopts it. Add a new version and a documented migration instead.
