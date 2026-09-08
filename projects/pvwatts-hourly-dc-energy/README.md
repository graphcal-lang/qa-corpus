# PVWatts hourly DC energy

This source-informed synthetic project asks: **How much DC energy does a 5 kW photovoltaic array produce over four one-hour conditions when the PVWatts module model is applied?**

It uses the published PVWatts Version 5 DC module equation with an original four-period profile. NREL does not publish expected values for these inputs, so the checked-in output is a stability baseline rather than a photovoltaic correctness claim. Its generation and determinism evidence are documented in [`reference/baseline.md`](reference/baseline.md).
