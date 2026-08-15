# FAO-56 reference-evapotranspiration source evidence

## Candidate generation

This source-backed candidate was prepared by an AI coding agent at the repository maintainer's direction from the cited public worked example. It does not derive from private material. Human source, privacy, adaptation, and promotion review remain pull-request responsibilities.

## Source and published expected values

R. G. Allen, L. S. Pereira, D. Raes, and M. Smith, *Crop Evapotranspiration: Guidelines for Computing Crop Water Requirements*, FAO Irrigation and Drainage Paper 56, Food and Agriculture Organization of the United Nations, Rome, 1998, Chapter 4, Equation 6 and Example 18, https://www.fao.org/4/x0490e/x0490e08.htm, accessed 2026-08-15.

For a daily time step, the source gives the FAO Penman–Monteith equation

\[
ET_0 =
\frac{
0.408\,\Delta(R_n-G)
+ \gamma\frac{900}{T+273}u_2(e_s-e_a)
}{
\Delta+\gamma(1+0.34u_2)
}.
\]

Example 18 publishes the rounded intermediate inputs reproduced by the project:

- \(T=16.9\ ^\circ\mathrm{C}\);
- \(u_2=2.078\ \mathrm{m/s}\);
- \(\Delta=0.122\ \mathrm{kPa/^{\circ}C}\);
- \(\gamma=0.0666\ \mathrm{kPa/^{\circ}C}\);
- \(e_s-e_a=0.589\ \mathrm{kPa}\);
- \(R_n=13.28\ \mathrm{MJ/(m^2\,day)}\);
- \(G=0\ \mathrm{MJ/(m^2\,day)}\).

The worked example then reports:

- radiation component: 2.81 mm/day;
- aerodynamic component: 1.07 mm/day;
- Equation 6 total before final presentation: 3.88 mm/day;
- final reported reference evapotranspiration: 3.9 mm/day.

Those four source-reported values—not locally calculated higher-precision values—are the manifest's expected values.

## Adaptation and source-to-assertion mapping

Graphcal intentionally has no affine Celsius unit. The project stores 16.9 °C as 290.05 K and explicitly obtains the conventional Celsius numeric value as \((T_K-273.15\,K)/(1\,K)\) before using the empirical \(T+273\) term. One degree Celsius and one kelvin have the same interval size, so \(\Delta\) and \(\gamma\) use kPa/K.

The empirical equation requires values normalized to its prescribed conventional units. The model makes those normalizations explicit, attaches mm/day to the output, and adds reporting nodes at the precision printed by Example 18.

The manifest maps the published outputs as follows:

- `/node/reported_radiation_component/display_value` = `2.81`;
- `/node/reported_aerodynamic_component/display_value` = `1.07`;
- `/node/reported_equation_reference_evapotranspiration/display_value` = `3.88`;
- `/node/reported_reference_evapotranspiration/display_value` = `3.9`;
- exact unit assertions require `mm_per_day`.

The unrounded internal nodes remain useful corpus coverage, but they are deliberately not reference-backed assertions because FAO does not report those extra digits.

## Licensing and adaptation

Only the equation and the small set of numerical facts needed for the cited worked result are reimplemented. No FAO prose, figures, calculation-sheet layout, software, or data files are copied. The Graphcal source and this evidence record are original corpus content under the repository license; the FAO publication is cited for provenance and is not relicensed here.
