# Graphcal QA Corpus

`qa-corpus` is a public collection of realistic Graphcal projects used for corpus-based compatibility, stability, and correctness testing. It is test data, not a performance benchmark and not a collection of user projects.

## What belongs here

Every project has one of two origins:

- **Source-backed reproduction:** a reimplementation of a reliable published or well-known engineering analysis. Independently verified assertions may make correctness claims. Citations, assumptions, adaptations, and redistributable inputs must be recorded.
- **Original synthetic complexity:** a new, imaginary engineering project designed to exercise realistic combinations of Graphcal features. Graphcal-produced expected output is a stability baseline, not proof that the engineering result is correct.

A project may combine independently verified reference assertions with stability baselines for other outputs. Each expectation must state which class it belongs to.

Private project names, paths, source text, inputs, outputs, and results are prohibited, even when edited or anonymized. See [PRIVACY.md](PRIVACY.md).

## Trust model

Coding agents and other generators may prepare **candidates**, but generated content is untrusted. A human promotes a candidate only after reviewing its privacy, structure, provenance, expectation classification, independent calculations, and determinism evidence. The complete process is in [CONTRIBUTING.md](CONTRIBUTING.md).

The corpus is data-only. Graphcal's trusted runner lives in the Graphcal repository and must not execute project-provided scripts. This repository's CI performs structural validation only; it does not invoke Graphcal or any program supplied by a corpus project.

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
├── schema/README.md            # bootstrap manifest contract
└── src/qa_corpus/              # trusted structural validator package
```

Projects are never discovered as runnable tests merely because they exist on disk. Every project, including quarantined candidates, and all of its QA cases must be declared in `corpus.toml`; only entries with `status = "active"` belong to the active corpus. Each case represents one entrypoint; a project may declare multiple cases only when it has multiple entry files.

## Validate locally

[`uv`](https://docs.astral.sh/uv/) installs the pinned Python 3.14 toolchain and test dependencies:

```console
$ uv run validate-corpus
Corpus structure is valid.
$ uv run -m pytest
```

The validator parses `corpus.toml` into strict Pydantic models and parses each `graphcal.toml`, then rejects invalid types, duplicate project or case identifiers, missing or undeclared projects, missing case entry files, malformed layout, symlinks, and paths that can escape this repository. It never executes project content.

## License

Original repository content is available under the [MIT License](LICENSE). A citation does not relicense its source: contributors must include only material they are entitled to redistribute and document any separately licensed inputs.
