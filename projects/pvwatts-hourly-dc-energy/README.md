# PVWatts hourly DC energy

This source-backed reproduction asks: **How much DC energy does a 5 kW photovoltaic array produce over four one-hour conditions when the PVWatts module model is applied?**

It reproduces only the PVWatts Version 5 DC module equation. Effective plane-of-array irradiance and cell temperature are already prepared inputs; the project does not model weather, optical losses, cell temperature, inverter conversion, clipping, or AC output. The asserted powers and energy are documented in [`reference/calculation.md`](reference/calculation.md).
