# FAO-56 daily reference evapotranspiration

This source-backed reproduction asks: **Does the FAO Penman–Monteith equation reproduce the daily reference evapotranspiration reported in FAO-56 Example 18?**

It evaluates Equation 6 from the rounded intermediate meteorological values published for the example and reports the result to 0.1 mm/day. Celsius is handled explicitly as a normalized numeric value while physical temperatures remain kelvin quantities. The source comparison, assumptions, unit adaptation, and independent calculation are documented in [`reference/calculation.md`](reference/calculation.md).
