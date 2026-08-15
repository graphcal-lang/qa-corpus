# Contributing to the Graphcal QA Corpus

Contributions are welcome when they add independently traceable correctness evidence or original, realistic Graphcal complexity without exposing private material.

## Candidate requirements

A candidate must be either:

1. a **source-backed reproduction** reimplemented from a reliable, redistributable published or well-known analysis; or
2. an **original synthetic complexity project** created without copying or transforming a private user project.

Do not submit a candidate merely because the current Graphcal implementation accepts it. Each project must answer a stated engineering question, exercise a documented feature or domain gap, and use deterministic checked-in inputs.

Initial corpus projects must not require network access, private or unpinned dependencies, native or WASM plugins, current time, randomness, or project-provided executable hooks.

## Candidate-to-active workflow

1. **Generate locally.** Humans or coding agents may create a candidate outside CI. Record the generator or author and the generation method.
2. **Perform privacy review.** Apply [PRIVACY.md](PRIVACY.md) to names, paths, comments, source, inputs, expected outputs, references, and history. Agent generation and automated scanning do not replace human inspection.
3. **Check structure.** Put the project at `projects/<domain>/<project>/`, add `graphcal.toml` and `qa.toml`, declare the exact path in `corpus.toml`, and run `uv run --locked scripts/validate_corpus.py`.
4. **Classify every expectation.** Use `reference-backed`, `stability-baseline`, or `health-only` according to the evidence described below. Do not present stability output as a correctness oracle.
5. **Verify evidence.** Independently check reference-backed assertions. Capture provenance and repeated-run determinism for stability baselines.
6. **Submit a pull request.** Explain the project's origin, purpose, coverage, evidence, licensing, and privacy review.
7. **Obtain human review.** At least one human other than the latest contributor must review the structural, technical, provenance, expectation, and privacy evidence before merge.

Coding-agent output remains an untrusted candidate until this process is complete.

## Expectation evidence

### Reference-backed

A reference-backed assertion must be supported by at least one of:

- an analytical calculation;
- a separately implemented reference calculation;
- a reliable published example with compatible assumptions; or
- manual verification by a domain expert.

Do not bless a value solely because `graphcal eval` produced it. Document formulas, assumptions, constants, sign and unit conventions, copied input data, adaptations, tolerances, and the independent result in `reference/calculation.md` or an equivalent non-executable record.

For a published source, include enough bibliographic detail to identify the exact example: author or organization, title, edition or version, page or section, DOI or stable URL when available, and access date where useful. Reimplement the analysis; do not copy copyrighted prose, figures, or substantial tables. Record the license and origin of any included third-party data.

### Stability baseline

A stability baseline detects behavioral drift and does not establish engineering correctness. Record:

- the exact Graphcal commit that produced it;
- the corpus candidate commit and case inputs;
- the normalized semantic JSON being compared;
- explicit comparison rules and floating-point tolerances; and
- evidence from repeated runs that the result is deterministic.

A baseline change requires a reviewed explanation of the intended semantic change. Mechanically replacing a snapshot because Graphcal emitted a different value is not acceptable.

### Health-only

A health-only case checks only an expected command outcome, such as successful parsing or checking. It makes no numerical correctness claim.

## Project and manifest rules

- Use stable lowercase kebab-case identifiers. Do not recycle an identifier for a different analysis.
- Keep each project under exactly `projects/<domain>/<project>/` and declare it in `corpus.toml`.
- Keep inputs and references in the project directory. Symbolic links are prohibited.
- Provide a short engineering question and document assumptions, constants, sign conventions, and unit conventions.
- Use narrowly justified per-assertion tolerances. Do not rely on a permissive global tolerance.
- Keep collection order significant where Graphcal defines it as significant; compare JSON objects semantically rather than by textual key order.
- Do not add scripts or hooks that corpus CI or the trusted Graphcal runner must execute.

The bootstrap schema is documented in [schema/README.md](schema/README.md). Schema evolution must remain coordinated with the trusted Graphcal runner.

## Pull request checklist

A project pull request must confirm that:

- [ ] the project origin is source-backed or original synthetic;
- [ ] no prohibited private names, paths, text, inputs, or results are present;
- [ ] all included source material and data may be redistributed;
- [ ] the project is explicitly declared and structural validation passes;
- [ ] every expectation has the correct evidence class;
- [ ] every reference-backed assertion was independently verified;
- [ ] every stability baseline records producing revisions, comparison rules, and repeated-run determinism;
- [ ] generation and human review provenance are documented; and
- [ ] the project requires no network, plugin, randomness, clock, private dependency, or executable project hook.

Maintainers may quarantine or reject a case whose provenance, privacy, determinism, or licensing cannot be established.
