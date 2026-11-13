# DOE series-impedance source evidence

## Candidate generation

This source-backed candidate was prepared by an AI coding agent at the repository maintainer's direction from the cited public U.S. Department of Energy handbook. It does not derive from private material. Human source, privacy, adaptation, and promotion review remain pull-request responsibilities.

## Source and published expected values

U.S. Department of Energy, *DOE Fundamentals Handbook: Electrical Science, Volume 3 of 4*, DOE-HDBK-1011/3-92, June 1992, Module 8, “Basic AC Reactive Components,” pages 11–14, https://www.energy.gov/sites/default/files/2026-04/DOE-HDBK-1011-92_VOL3.pdf, accessed 2026-08-16.

The handbook describes impedance as the phasor sum of resistance and reactance and publishes these worked examples:

- `R = 100 Ω`, `XL = 60 Ω`, producing `Z = 116.6 Ω` for a series R–L circuit;
- `R = 60 Ω`, `XC = 50 Ω`, producing `Z = 78.1 Ω` for a series R–C circuit;
- `R = 6 Ω`, `XL = 20 Ω`, and `XC = 10 Ω`, producing `Z = 11.66 Ω` for a series R–C–L circuit.

Those three DOE-reported magnitudes—not locally generated extra digits—are the reference expectations.

## Adaptation and source-to-assertion mapping

The reusable `series_impedance` DAG constructs

\[
Z = R + j(X_L-X_C).
\]

This signed rectangular form preserves the handbook's phasor description: inductive reactance is positive imaginary and capacitive reactance is negative imaginary. `abs(Z)` is the handbook's \(\sqrt{R^2+(X_L-X_C)^2}\). Reporting nodes round to exactly the number of decimal places printed by DOE.

The manifest maps the source outputs as:

- `/node/reported_rl_impedance/display_value` = `116.6` Ω;
- `/node/reported_rc_impedance/display_value` = `78.1` Ω;
- `/node/reported_rcl_impedance/display_value` = `11.66` Ω;
- each corresponding `/unit` value is `ohm`.

The tolerances cover only binary representation at less than half of the source's final reported increment.

## Graphcal feature coverage

This project intentionally exercises features absent from the preceding corpus:

- user-defined `Voltage` and `Resistance` dimensions and units;
- `Complex<Resistance>` and `Complex<ElectricCurrent>` values;
- `complex`, `to_complex`, `re`, `im`, `abs`, `phase`, `conj`, and `polar`;
- real-by-complex division for the R–L current phasor;
- constrained top-level inputs, a reusable multi-output `dag` with a required dimension port, and three aliased `include` instances;
- in-language tolerance assertions.

Current, phase, conjugate, and reconstructed-polar nodes are feature checks only. They are not reference assertions because the cited worked examples do not print those outputs.

## Licensing and adaptation

The DOE document states that it is approved for public release with unlimited distribution. Only three short numerical examples and their governing phasor relation are reimplemented; no figures or substantial prose are copied. The Graphcal source and this evidence record are original corpus content under the repository license, while the handbook remains cited external source material.
