# Stability baseline evidence

## Classification and generation

This is an original synthetic, source-informed project prepared as a candidate by an AI coding agent at the repository maintainer's direction. NREL publishes the PVWatts Version 5 module equation, but it does not publish expected outputs for this project's invented four-period irradiance and temperature profile. The checked-in output is therefore a Graphcal stability baseline, not a photovoltaic correctness oracle. The project does not derive from private material. Human privacy, technical, and promotion review remain pull-request responsibilities.

## Producing revisions and inputs

- Graphcal: `0.0.1-alpha.23`, commit `04ab7150534de0b795acae1b3a7bcc282266ec3c`
- Corpus source revision: `42259833d1b8d6c60c761195a4a7981019058e17`
- Entrypoint: `src/pvwatts_hourly_dc_energy/main.gcl`
- Inputs: checked-in parameter defaults; no `--set` or `--input` overrides
- Expected output: `expected/four-hour-profile.json`
- Canonical expected-output SHA-256: `0b9d5330bcb9ae8cdb30f9971b97a0420e518fe72c05a676b85692bcba087a44`

The source equation is A. P. Dobos, *PVWatts Version 5 Manual*, NREL/TP-6A20-62641, September 2014, Section 10, Equation 8, DOI [10.2172/1158421](https://doi.org/10.2172/1158421). That citation motivates the model but does not supply its expected values.

The baseline was generated from the project directory with:

```console
graphcal eval --format json --root . src/pvwatts_hourly_dc_energy/main.gcl \
  | jq -S . > expected/four-hour-profile.json
```

## Comparison rules

The runner parses both outputs as strict JSON and compares them semantically. Object key order is ignored; array order and length are significant; missing or additional values fail; and JSON values compare exactly by type and value. This baseline declares no numeric tolerances.

Exact comparison intentionally detects deterministic changes across indexed calculations, temperature differences, aggregation, and custom energy-unit display. It does not prove that the synthetic operating profile or its outputs match a published PV system.

## Repeated-run determinism

Five consecutive evaluations with the recorded Graphcal executable and source revision produced the same canonical semantic JSON. Each result was canonicalized with `jq -S -c` and hashed with SHA-256:

```text
0b9d5330bcb9ae8cdb30f9971b97a0420e518fe72c05a676b85692bcba087a44
0b9d5330bcb9ae8cdb30f9971b97a0420e518fe72c05a676b85692bcba087a44
0b9d5330bcb9ae8cdb30f9971b97a0420e518fe72c05a676b85692bcba087a44
0b9d5330bcb9ae8cdb30f9971b97a0420e518fe72c05a676b85692bcba087a44
0b9d5330bcb9ae8cdb30f9971b97a0420e518fe72c05a676b85692bcba087a44
```

This establishes repeatability only for the recorded executable and inputs.
