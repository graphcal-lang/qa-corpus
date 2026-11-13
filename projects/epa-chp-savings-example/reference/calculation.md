# EPA CHP savings source evidence

## Candidate generation

This source-backed candidate was prepared by an AI coding agent at the repository maintainer's direction from the cited public U.S. EPA worked example. It does not derive from private material. Human source, privacy, adaptation, and promotion review remain pull-request responsibilities.

## Source and published expected values

U.S. Environmental Protection Agency Combined Heat and Power Partnership, *Fuel and Carbon Dioxide Emissions Savings Calculation Methodology for Combined Heat and Power Systems*, June 2021, Appendix A, especially pages 20–21, https://www.epa.gov/sites/default/files/2015-07/documents/fuel_and_carbon_dioxide_emissions_savings_calculation_methodology_for_combined_heat_and_power_systems.pdf, accessed 2026-08-16.

Appendix A publishes a complete CEESC example. Its Equation 1 reports total fuel savings as

\[
115{,}546=(257{,}964+300{,}437)-442{,}855\ \text{MMBtu/year}.
\]

Its Equation 2 reports total carbon-dioxide savings as

\[
18{,}065=(15{,}078+28{,}872)-25{,}885\ \text{tons CO}_2/\text{year}.
\]

Table 1 on page 20 also reports fuel savings of 115,546 MMBtu/year and 21%.

These EPA-reported values—not locally generated higher-precision outputs—are the manifest's expected values.

## Adaptation and source-to-assertion mapping

The source quantities are annual totals. The Graphcal project represents the one-year fuel totals as `Energy` and CO₂ totals as `Mass`; it does not divide both sides by a year because that common reporting interval cancels in the savings equations.

`MMBtu` is represented using the international-table Btu conversion, and `short_ton` uses the U.S. short ton. Conversion provenance is recorded by NIST, *Guide to the SI*, Appendix B.8, https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b8. The assertions target source-unit display values so SI conversion does not become the numerical oracle.

The manifest maps the source values as follows:

- `/node/total_fuel_savings/display_value` = `115546.0` MMBtu, from Appendix A Equation 1 and Table 1;
- `/node/reported_fuel_savings_percent/si_value` = `21.0`, from Appendix A Table 1;
- `/node/total_co2_savings/display_value` = `18065.0` short tons, from Appendix A Equation 2;
- exact unit-label assertions distinguish the source-unit presentations.

Small absolute tolerances on the two display values cover only binary floating-point roundoff introduced by unit scaling. They do not widen the source's published whole-unit precision.

The report notes that some detailed figures do not equate exactly because of rounding. This project intentionally reproduces the rounded Equation 1 and Equation 2 arithmetic rather than claiming unreported precision.

## Licensing and adaptation

Only the equations and the small set of numerical facts needed for the cited worked result are reimplemented. No EPA prose, figures, calculator software, or substantial tables are copied. The Graphcal source and this evidence record are original corpus content under the repository license; the EPA and NIST pages are cited for provenance and are not relicensed here.
