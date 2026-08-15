# Independent ideal rocket equation calculation

## Candidate generation

This source-backed candidate was prepared by an AI coding agent at the repository maintainer's direction. The agent selected the cited public formulas, wrote an original Graphcal reproduction, and performed the separate Python calculation below. It does not derive from a private project. Human source, privacy, calculation, and promotion review remain pull-request responsibilities.

## Source

NASA Glenn Research Center, “Ideal Rocket Equation,” *Beginner's Guide to Aeronautics*, https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/ideal-rocket-equation/, accessed 2026-08-15.

NASA derives

\[
\Delta v = I_{sp} g_0 \ln(MR), \qquad MR = \frac{m_{initial}}{m_{final}}.
\]

The source explicitly treats this as an ideal equation and neglects aerodynamic lift and drag and, in the form reproduced here, gravity losses.

The conventional standard acceleration is from the 3rd General Conference on Weights and Measures, Declaration 2 (1901), DOI [10.59161/CGPM1901DECL2E](https://doi.org/10.59161/CGPM1901DECL2E): 980.665 cm/s², exactly 9.80665 m/s².

## Adapted inputs

- Empty/final mass: 10,000 kg
- Propellant mass: 90,000 kg
- Initial mass: 100,000 kg
- Specific impulse: 350 s
- Standard acceleration: 9.80665 m/s²

Mass is treated as constant empty mass plus completely consumed propellant. No staging, residual propellant, gravity loss, drag loss, steering loss, or atmosphere-dependent specific impulse is modeled.

## Independent calculation

Using Python 3.14's standard-library `math.log` with ordinary double-precision arithmetic, independently of Graphcal:

\[
MR = \frac{100000}{10000} = 10
\]

\[
V_{eq} = 350 \times 9.80665 = 3432.3275\ \text{m/s}
\]

\[
\Delta v = 3432.3275 \times \ln(10)
         = 7903.226135773521\ \text{m/s}
\]

The manifest assertions use an absolute tolerance of 1 × 10⁻⁹ m/s for the two floating-point velocity values and exact comparison for the mass ratio and output unit. The tolerance is several orders of magnitude below meaningful engineering precision while allowing the last binary floating-point digits to differ.

## Licensing and adaptation

The formulas were reimplemented from the cited NASA educational page; no source prose, figures, or tabular data are reproduced. This repository's source and calculation record are original text under the repository license. NASA’s page is cited for provenance and is not relicensed here.
