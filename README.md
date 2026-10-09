# Graphcal QA Corpus

`qa-corpus` is a public collection of realistic Graphcal projects used for corpus-based compatibility, stability, and correctness testing. It is test data, not a performance benchmark and not a collection of user projects.

## What belongs here

Every project has one of two origins:

- **Source-backed reproduction:** a reliable public source supplies both the reproduced inputs and the correct output values. Reference-backed assertions must trace directly to values reported by that source, including any explicit source rounding or documented unit conversion.
- **Original synthetic complexity:** a new scenario designed to exercise realistic combinations of Graphcal features. This includes source-informed models that reuse a published equation with original or adapted inputs when the source does not report the corresponding outputs. Graphcal-produced expected output is a stability baseline, not proof that the engineering result is correct.

A published equation alone does not make a case source-backed. A local analytical calculation, separate implementation, or domain review may corroborate a source value, but it cannot be the sole oracle for a reference-backed assertion. Each case has one expectation class; a project with multiple entrypoints may use different classes only when each case independently satisfies its evidence contract.

Private project names, paths, source text, inputs, outputs, and results are prohibited, even when edited or anonymized. See [PRIVACY.md](PRIVACY.md).

## Trust model

Coding agents and other generators may prepare **candidates**, but generated content is untrusted. A human promotes a candidate only after reviewing its privacy, structure, provenance, expectation classification, source-to-assertion traceability, and determinism evidence. The complete process is in [CONTRIBUTING.md](CONTRIBUTING.md).

Corpus projects are data-only and must not contain executable test hooks. This repository provides an opt-in local runner for a caller-supplied Graphcal executable; it never invokes project-provided programs. Repository CI performs structural validation only and does not run Graphcal.

## Repository layout

```text
.
├── corpus.toml                 # project inventory and QA cases
├── projects/
│   └── <project-id>/
│       ├── graphcal.toml       # Graphcal project manifest
│       ├── src/
│       ├── inputs/
│       ├── expected/
│       └── reference/
├── schema/README.md            # versioned manifest and expectation contract
└── src/qa_corpus/              # structural validator and local executable runner
```

Projects are never discovered as runnable tests merely because they exist on disk. Every project, including quarantined candidates, and all of its QA cases must be declared in `corpus.toml`; only entries with `status = "active"` belong to the active corpus. Each case represents one entrypoint; a project may declare multiple cases only when it has multiple entry files.

## Validate locally

[`uv`](https://docs.astral.sh/uv/) installs the pinned Python 3.14 toolchain and test dependencies:

```console
$ uv run validate-corpus
Corpus structure is valid.
$ uv run -m pytest
```

The validator parses `corpus.toml` into strict Pydantic models and parses each `graphcal.toml` and stability-baseline JSON file. It rejects invalid types, duplicate identifiers, missing or undeclared files, malformed expectations, invalid JSON Pointers, symlinks, and paths that can escape this repository. It never executes project content.

## Test a Graphcal executable

Run the active corpus against a local Graphcal build by passing its executable path or command name:

```console
$ uv run test-graphcal /path/to/graphcal > report.json
```

The command first validates the repository. For each active case, in manifest order, it runs `graphcal format --check`, `graphcal check`, and `graphcal eval --format json` from the project directory. Evaluation is skipped when checking fails. Each process has a 30-second timeout by default; use `--timeout SECONDS` to change it.

After evaluation, the runner applies each case's typed expectation: pipeline success for `health-only`, semantic JSON comparison for `stability-baseline`, or JSON Pointer assertions for `reference-backed`. Stdout contains only one versioned JSON report with overall status, summary counts, per-stage exit codes and captured output, parsed evaluation results, and expectation issues. The command exits zero only when every stage and expectation for every active case passes. Quarantined projects are not run.

The corpus includes one minimal active example of each expectation class. See [`schema/README.md`](schema/README.md) for the complete manifest and comparison contract.

## License

Original repository content is available under the [MIT License](LICENSE). A citation does not relicense its source: contributors must include only material they are entitled to redistribute and document any separately licensed inputs.
