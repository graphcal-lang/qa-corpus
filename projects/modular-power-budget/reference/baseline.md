# Stability baseline evidence

## Classification and generation

This project is original synthetic content prepared as a candidate by an AI coding agent at the repository maintainer's direction. It models invented loads and does not derive from a private or third-party project. Human privacy, technical, and promotion review remain pull-request responsibilities.

## Producing revisions and inputs

- Graphcal: `0.0.1-alpha.23`, commit `ccde51967e113dd9322b35be2cda81b78a573138`
- Corpus source and expected-output content: commit `596b30658145f4fca7816986b8f80287d4a23eac`
- Entrypoint: `src/modular_power_budget/main.gcl`
- Included module: `src/modular_power_budget/loads.gcl`
- Inputs: the checked-in parameter defaults; no `--set` or `--input` overrides
- Expected output: `expected/nominal.json`

The baseline was generated with:

```console
graphcal eval --format json \
  --root projects/modular-power-budget \
  projects/modular-power-budget/src/modular_power_budget/main.gcl
```

## Comparison rules

The runner parses both outputs as strict JSON and compares them semantically:

- JSON object key order is ignored.
- JSON array order and length are significant.
- Missing and additional values fail comparison.
- Strings, booleans, and null values compare exactly by type and value.
- JSON numbers compare exactly unless a JSON Pointer has an explicit numeric tolerance.
- This baseline declares no tolerances; all numbers therefore compare exactly.

Exact comparison is intentional because the arithmetic uses values selected to produce stable finite results. A future tolerance must identify one numeric JSON Pointer and justify every nonzero absolute or relative bound it declares.

## Repeated-run determinism

Five consecutive evaluations with Graphcal commit `ccde51967e113dd9322b35be2cda81b78a573138` produced the same canonical semantic JSON. Each result was canonicalized with `jq -S -c` and hashed with SHA-256:

```text
5f0767758233ac7e8ac1f94d82f85e7817a25c0f2ff677c50d9d5e4bf34ff239
5f0767758233ac7e8ac1f94d82f85e7817a25c0f2ff677c50d9d5e4bf34ff239
5f0767758233ac7e8ac1f94d82f85e7817a25c0f2ff677c50d9d5e4bf34ff239
5f0767758233ac7e8ac1f94d82f85e7817a25c0f2ff677c50d9d5e4bf34ff239
5f0767758233ac7e8ac1f94d82f85e7817a25c0f2ff677c50d9d5e4bf34ff239
```

This establishes repeatability for the recorded executable and inputs. It does not establish engineering correctness.
