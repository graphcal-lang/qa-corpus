# Stability baseline evidence

## Classification and generation

This is an original synthetic, source-informed project prepared as a candidate by an AI coding agent at the repository maintainer's direction. NASA publishes the lift and dynamic-pressure equations, but it does not publish expected outputs for this project's invented density, wing, coefficient, speeds, and required lift. The checked-in output is therefore a Graphcal stability baseline, not an aerodynamic correctness oracle. The project does not derive from private material. Human privacy, technical, and promotion review remain pull-request responsibilities.

## Producing revisions and inputs

- Graphcal: `0.0.1-alpha.23`, commit `04ab7150534de0b795acae1b3a7bcc282266ec3c`
- Corpus source revision: `42259833d1b8d6c60c761195a4a7981019058e17`
- Entrypoint: `src/nasa_lift_sweep/main.gcl`
- Inputs: checked-in parameter defaults; no `--set` or `--input` overrides
- Expected output: `expected/three-flight-points.json`
- Canonical expected-output SHA-256: `c06e90a3f2e52cd3a621bb2a2c49e7beea35a5413059288105d25dbe354bf299`

The source equations are documented by NASA Glenn Research Center, “Lift Coefficient,” *Beginner's Guide to Aeronautics*, https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-coefficient/, accessed 2026-08-15. That citation motivates the model but does not supply its expected values.

The baseline was generated from the project directory with:

```console
graphcal eval --format json --root . src/nasa_lift_sweep/main.gcl \
  | jq -S . > expected/three-flight-points.json
```

## Comparison rules

The runner parses both outputs as strict JSON and compares them semantically. Object key order is ignored; array order and length are significant; missing or additional values fail; and JSON values compare exactly by type and value. This baseline declares no numeric tolerances.

Exact comparison intentionally detects deterministic changes across indexed evaluation, powers, reductions, square roots, and unit display. It does not prove that the synthetic aerodynamic assumptions are correct.

## Repeated-run determinism

Five consecutive evaluations with the recorded Graphcal executable and source revision produced the same canonical semantic JSON. Each result was canonicalized with `jq -S -c` and hashed with SHA-256:

```text
c06e90a3f2e52cd3a621bb2a2c49e7beea35a5413059288105d25dbe354bf299
c06e90a3f2e52cd3a621bb2a2c49e7beea35a5413059288105d25dbe354bf299
c06e90a3f2e52cd3a621bb2a2c49e7beea35a5413059288105d25dbe354bf299
c06e90a3f2e52cd3a621bb2a2c49e7beea35a5413059288105d25dbe354bf299
c06e90a3f2e52cd3a621bb2a2c49e7beea35a5413059288105d25dbe354bf299
```

This establishes repeatability only for the recorded executable and inputs.
