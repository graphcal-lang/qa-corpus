# Contributing to the Graphcal QA Corpus

Contributions are welcome when they add directly source-traceable correctness evidence or original, realistic Graphcal complexity without exposing private material.

## Candidate requirements

A candidate must be either:

1. a **source-backed reproduction** for which a reliable, redistributable public source supplies both the reproduced inputs and the expected output values; or
2. an **original synthetic complexity project** created without copying or transforming a private user project.

A project that applies a published equation to original or adapted inputs is original synthetic unless the source also reports the corresponding output. Such a case may cite the equation, but its Graphcal-produced output must be classified as a stability baseline.

Do not submit a candidate merely because the current Graphcal implementation accepts it. Each project must answer a stated engineering question, exercise a documented feature or domain gap, and use deterministic checked-in inputs.

Initial corpus projects must not require network access, private or unpinned dependencies, native or WASM plugins, current time, randomness, or project-provided executable hooks.

## Candidate-to-active workflow

1. **Generate locally.** Humans or coding agents may create a candidate outside CI. Record the generator or author and the generation method.
2. **Perform privacy review.** Apply [PRIVACY.md](PRIVACY.md) to names, paths, comments, source, inputs, expected outputs, references, and history. Agent generation and automated scanning do not replace human inspection.
3. **Check structure.** Put the project at `projects/<project-id>/`, add `graphcal.toml`, declare the project and all QA cases in `corpus.toml`, and run `uv run validate-corpus`.
4. **Classify every expectation.** Use `reference-backed`, `stability-baseline`, or `health-only` according to the evidence described below. Do not present stability output as a correctness oracle.
5. **Verify evidence.** Trace every reference-backed expected value to the exact public source location that reports it. Capture producing revisions and repeated-run determinism for stability baselines.
6. **Submit a pull request.** Explain the project's origin, purpose, coverage, evidence, licensing, and privacy review.
7. **Obtain human review.** At least one human other than the latest contributor must review the structural, technical, provenance, expectation, and privacy evidence before merge.

Coding-agent output remains an untrusted candidate until this process is complete.

## Expectation evidence

### Reference-backed

A reference-backed assertion requires a reliable public source that reports both:

- the inputs and assumptions reproduced by the case; and
- the expected numerical or scalar output asserted by the manifest.

The evidence must map each JSON Pointer and expected value to an exact source location such as a worked example, report table, published test vector, or source-maintained reference output. Assert only the precision the source reports. Document any source-prescribed rounding and any lossless unit or representation conversion.

An analytical calculation, separately implemented calculation, domain-expert review, or agreement with `graphcal eval` may corroborate a published value, but none is sufficient as the sole oracle. If a source publishes an equation but no output for the case's inputs, classify the case as `stability-baseline`, not `reference-backed`.

Include enough bibliographic detail to identify the exact example: author or organization, title, edition or version, page, table, equation, or section, DOI or stable URL when available, and access date where useful. Reimplement the analysis; do not copy copyrighted prose, figures, or substantial tables. Record the license and origin of any included third-party data.

### Stability baseline

A stability baseline detects behavioral drift and does not establish engineering correctness. Use it for original synthetic cases and source-informed cases whose references provide equations or methods but no expected values for the reproduced inputs. Record:

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
- Keep each project under exactly `projects/<project-id>/`, with the directory name matching the project ID, and declare it in `corpus.toml`.
- Declare one case per entrypoint under its project in `corpus.toml`; do not create separate checking, formatting, and evaluation cases for the same entry file.
- Keep inputs and references in the project directory. Symbolic links are prohibited.
- Provide a short engineering question and document assumptions, constants, sign conventions, and unit conventions.
- Use narrowly justified per-assertion tolerances. Do not rely on a permissive global tolerance.
- Keep collection order significant where Graphcal defines it as significant; compare JSON objects semantically rather than by textual key order.
- Do not add scripts or hooks that corpus CI or the trusted Graphcal runner must execute.

The versioned manifest and expectation schema is documented in [schema/README.md](schema/README.md). Schema evolution must remain coordinated with runner consumers.

## Pull request checklist

A project pull request must confirm that:

- [ ] the project origin is source-backed or original synthetic;
- [ ] no prohibited private names, paths, text, inputs, or results are present;
- [ ] all included source material and data may be redistributed;
- [ ] the project is explicitly declared and structural validation passes;
- [ ] every expectation has the correct evidence class;
- [ ] every reference-backed assertion maps directly to a value reported by a reliable public source;
- [ ] every stability baseline records producing revisions, comparison rules, and repeated-run determinism;
- [ ] generation and human review provenance are documented; and
- [ ] the project requires no network, plugin, randomness, clock, private dependency, or executable project hook.

Maintainers may quarantine or reject a case whose provenance, privacy, determinism, or licensing cannot be established.
