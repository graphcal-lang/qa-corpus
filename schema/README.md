# Bootstrap manifest schema

This document defines schema version 1 for structural validation. The trusted Graphcal runner will own the complete typed case and assertion schema in a later phase; fields not needed for bootstrap validation are intentionally deferred.

## `corpus.toml`

The root manifest is the only project inventory. It contains:

```toml
schema_version = 1

[[projects]]
id = "rocket-stage-sizing"
path = "projects/propulsion/rocket-stage-sizing"
status = "active"
```

Rules:

- `schema_version` must be the integer `1`.
- `projects` must be an array of tables (or `[]` for an empty corpus).
- `id` is a repository-wide, stable lowercase kebab-case identifier.
- `path` is a canonical repository-relative POSIX path with exactly the form `projects/<domain>/<project>`.
- `status` is `active` or `quarantined`.
- Project identifiers and paths must be unique.
- Every listed path must exist and contain `graphcal.toml` and `qa.toml`.
- Every directory at `projects/<domain>/<project>` must be listed, even when quarantined. Directories never become active by discovery.
- Absolute paths, `.` or `..` components, backslashes, symbolic links, and any path resolving outside the repository are invalid.

To add the first project, remove `projects = []` before adding `[[projects]]` tables.

## Project `qa.toml`

The bootstrap validator requires only the structural identity fields:

```toml
schema_version = 1

[project]
id = "rocket-stage-sizing"
```

The `project.id` must match the declaring `corpus.toml` entry. Additional provenance, cases, assertions, comparison profiles, and evidence may be added as tables, but their stable typed representation will be finalized with the trusted runner. Until then, contributions must still document all evidence required by [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

The validator also parses `graphcal.toml` as TOML but does not interpret it and never invokes Graphcal.

## Versioning

A schema version denotes a contract shared with the Graphcal-side runner. Do not change the meaning of version 1 in place after that runner adopts it. Add a new version and a documented migration instead.
