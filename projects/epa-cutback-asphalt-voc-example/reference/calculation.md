# EPA cutback-asphalt VOC source evidence

## Candidate generation

This source-backed candidate was prepared by an AI coding agent at the repository maintainer's direction from the cited public U.S. Environmental Protection Agency worked example. It does not derive from private material. Human source, privacy, adaptation, and promotion review remain pull-request responsibilities.

## Source and published expected values

U.S. Environmental Protection Agency, AP-42, Volume I, Chapter 4.5, “Asphalt Paving Operations,” Section 4.5.2, worked example on page 4.5-2, July 1979, reformatted January 1995, https://www.epa.gov/sites/default/files/2020-10/documents/c4s05.pdf, accessed 2026-08-16.

The example uses:

- 10,000 kg of rapid-cure cutback asphalt;
- 45% diluent by volume;
- diluent density of 0.7 kg/L;
- asphalt-cement density of 1.1 kg/L; and
- 95% of the diluent mass treated as evaporative VOC.

The source solves the total-mass and volume-fraction equations and reports approximately:

- 4,900 L of diluent;
- 3,400 kg of diluent;
- 3,200 kg of emitted VOC; and
- 32% of the cutback-asphalt mass emitted as VOC.

Those four EPA-reported values—not locally generated higher-precision results—are the manifest's expected values.

## Adaptation and source-to-assertion mapping

Writing diluent volume as \(x\), asphalt-cement volume as \(y\), total mass as \(M\), diluent volume fraction as \(f\), and the two densities as \(\rho_d\) and \(\rho_a\), the source equations are

\[
M=\rho_dx+\rho_ay, \qquad x=f(x+y).
\]

The model eliminates \(y\) to evaluate the same system. EPA reports staged approximate values: it first rounds diluent volume and mass, then multiplies the reported 3,400 kg by 0.95 and reports 3,200 kg. The Graphcal reporting nodes intentionally preserve that sequence instead of asserting local extra precision.

The manifest maps the source outputs as:

- `/node/reported_diluent_volume/display_value` = `4900.0` L;
- `/node/reported_diluent_mass/display_value` = `3400.0` kg;
- `/node/reported_voc_mass/display_value` = `3200.0` kg;
- `/node/reported_voc_percent_by_mass/si_value` = `32.0`;
- exact unit assertions require `L` and `kg` where applicable.

Narrow display-value tolerances cover only binary unit-scaling representation and do not widen the source's hundred-unit precision.

## Licensing and adaptation

Only the equations and small set of numerical facts needed for the cited worked result are reimplemented. No EPA prose, figure, software, or substantial table is copied. The Graphcal source and this evidence record are original corpus content under the repository license; the EPA publication is cited for provenance and is not relicensed here.
