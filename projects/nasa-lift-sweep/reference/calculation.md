# Independent NASA lift-equation calculation

## Candidate generation

This source-backed candidate was prepared by an AI coding agent at the repository maintainer's direction. The agent selected the cited public formula, chose original illustrative inputs, wrote an original Graphcal reproduction, and performed the separate calculation below. It does not derive from a private project. Human source, privacy, calculation, and promotion review remain pull-request responsibilities.

## Source

NASA Glenn Research Center, “Lift Coefficient,” *Beginner's Guide to Aeronautics*, https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-coefficient/, accessed 2026-08-15.

NASA states that dynamic pressure and lift coefficient satisfy

\[
q = \frac{1}{2}\rho V^2, \qquad C_l = \frac{L}{qA}.
\]

Rearranging the second equation gives \(L=C_l qA\). Solving the combined equation for the speed that produces a specified lift gives

\[
V = \sqrt{\frac{2L}{\rho A C_l}}.
\]

The source cautions that a lift coefficient carries shape, viscosity, and compressibility effects. This reproduction deliberately holds it constant and uses low-speed points; it does not model those effects.

## Adapted inputs

These values are illustrative inputs created for this corpus project, not a copied NASA example:

- air density: 1.225 kg/m³;
- wing area: 16.2 m²;
- lift coefficient: 0.8;
- airspeeds: 30, 40, and 50 m/s;
- required lift for the inverse calculation: 12,000 N.

The model assumes steady conditions and uses one constant density, area, and lift coefficient at every flight point.

## Independent calculation

Using the formulas above with ordinary binary64 arithmetic, independently of Graphcal:

| Speed (m/s) | \(q=\rho V^2/2\) (Pa) | \(L=C_lqA\) (N) |
|---:|---:|---:|
| 30 | 551.25 | 7,144.2 |
| 40 | 980.0 | 12,700.8 |
| 50 | 1,531.25 | 19,845.0 |

For the required-lift calculation:

\[
V = \sqrt{\frac{2(12000)}{(1.225)(16.2)(0.8)}}
  = 38.88078956798696\ \text{m/s}.
\]

The manifest checks the 40 m/s dynamic pressure, the 40 m/s lift, the maximum sweep lift, and the inverse speed. Absolute tolerances of 1 × 10⁻⁹ in each asserted SI value allow only last-bit floating-point differences.

## Licensing and adaptation

The equations were reimplemented from the cited NASA educational page. No source prose, figures, software, or data files are reproduced. All numerical inputs and explanatory text in this project are original corpus material under the repository license; the NASA page is cited for provenance and is not relicensed here.
