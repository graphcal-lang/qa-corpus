# Independent FAO-56 reference-evapotranspiration calculation

## Candidate generation

This source-backed candidate was prepared by an AI coding agent at the repository maintainer's direction. The agent selected the cited public worked example, wrote an original Graphcal reproduction from its formula and rounded intermediate values, and performed the separate calculation below. It does not derive from a private project. Human source, privacy, calculation, and promotion review remain pull-request responsibilities.

## Source

R. G. Allen, L. S. Pereira, D. Raes, and M. Smith, *Crop Evapotranspiration: Guidelines for Computing Crop Water Requirements*, FAO Irrigation and Drainage Paper 56, Food and Agriculture Organization of the United Nations, Rome, 1998, Chapter 4, Equation 6 and Example 18, https://www.fao.org/4/x0490e/x0490e08.htm, accessed 2026-08-15.

For a daily time step, the FAO Penman–Monteith equation is

\[
ET_0 =
\frac{
0.408\,\Delta(R_n-G)
+ \gamma\frac{900}{T+273}u_2(e_s-e_a)
}{
\Delta+\gamma(1+0.34u_2)
}.
\]

Under the equation's stated conventional units, the result is millimetres per day. Example 18 reports 3.88 mm/day before presenting the result as 3.9 mm/day.

## Reproduced inputs and adaptations

This project begins from the rounded intermediate values printed in Example 18:

- mean air temperature \(T=16.9\ ^\circ\mathrm{C}\);
- wind speed at 2 m \(u_2=2.078\ \mathrm{m/s}\);
- slope of the vapour-pressure curve \(\Delta=0.122\ \mathrm{kPa/K}\);
- psychrometric constant \(\gamma=0.0666\ \mathrm{kPa/K}\);
- vapour-pressure deficit \(e_s-e_a=0.589\ \mathrm{kPa}\);
- net radiation \(R_n=13.28\ \mathrm{MJ/(m^2\,day)}\);
- daily soil heat flux \(G=0\ \mathrm{MJ/(m^2\,day)}\).

The example's intermediate values are already rounded, so this is a reproduction of its final Equation 6 calculation, not a recomputation from the raw weather observations.

Graphcal intentionally has no affine Celsius unit. The model stores 16.9 °C as 290.05 K and explicitly computes the Celsius numeric value as \((T_K-273.15\,K)/(1\,K)\) before using the empirical \(T+273\) term. Temperature differences in \(\Delta\) and \(\gamma\) use kelvin because one kelvin and one degree Celsius have the same interval size.

The empirical equation combines values expressed in prescribed conventional units. The Graphcal model makes each normalization explicit, computes the conventional numerical terms dimensionlessly, and attaches the physical output unit mm/day.

## Independent calculation

Using the published rounded values with ordinary binary64 arithmetic, independently of Graphcal:

\[
D = 0.122 + 0.0666(1+0.34(2.078))
  = 0.23565423200000002.
\]

Radiation component:

\[
ET_{rad} = \frac{0.408(13.28)(0.122)}{D}
         = 2.805064328316411\ \mathrm{mm/day}.
\]

Aerodynamic component:

\[
ET_{aero} =
\frac{0.0666\,[900/(16.9+273)](2.078)(0.589)}{D}
=1.073875953888906\ \mathrm{mm/day}.
\]

Therefore:

\[
ET_0=3.878940282205317\ \mathrm{mm/day},
\]

which rounds to 3.9 mm/day and agrees with the reported Example 18 result. Using \(1\ \mathrm{mm/day}=10^{-3}/86400\ \mathrm{m/s}\), the corresponding SI values are:

- radiation component: 3.2466022318476985 × 10⁻⁸ m/s;
- aerodynamic component: 1.2429119836677152 × 10⁻⁸ m/s;
- unrounded total: 4.489514215515413 × 10⁻⁸ m/s;
- reported 3.9 mm/day: 4.5138888888888884 × 10⁻⁸ m/s.

The manifest checks these SI values with narrowly scoped tolerances and checks the displayed mm/day unit exactly.

## Licensing and adaptation

Only the equation and the small set of numerical facts needed to reproduce the cited worked example are used. No FAO prose, figures, calculation-sheet layout, software, or data files are copied. The Graphcal implementation and this explanation are original corpus content under the repository license; the FAO publication is cited for provenance and is not relicensed here.
