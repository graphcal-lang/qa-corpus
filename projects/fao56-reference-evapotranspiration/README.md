# FAO-56 daily reference evapotranspiration

This source-backed reproduction asks: **Does the FAO Penman–Monteith equation reproduce the daily reference evapotranspiration reported in FAO-56 Example 18?**

It evaluates Equation 6 from the rounded intermediate meteorological values published for the example and exposes results at the precision printed by FAO. Celsius is handled explicitly as a normalized numeric value while physical temperatures remain kelvin quantities. The source-to-assertion mapping and unit adaptation are documented in [`reference/calculation.md`](reference/calculation.md).
