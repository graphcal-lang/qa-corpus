# Independent PVWatts hourly DC-energy calculation

## Candidate generation

This source-backed candidate was prepared by an AI coding agent at the repository maintainer's direction. The agent selected the cited public model, created a small deterministic set of illustrative operating points, wrote an original Graphcal reproduction, and performed the separate calculation below. It does not derive from a private project. Human source, privacy, calculation, and promotion review remain pull-request responsibilities.

## Source

A. P. Dobos, *PVWatts Version 5 Manual*, National Renewable Energy Laboratory, NREL/TP-6A20-62641, September 2014, Section 10, Equation 8, DOI [10.2172/1158421](https://doi.org/10.2172/1158421), https://www.osti.gov/biblio/1158421, accessed 2026-08-15.

The report defines the DC module model as

\[
P_{dc}=\frac{I_{tr}}{1000}P_{dc0}
       \left[1+\gamma(T_{cell}-T_{ref})\right],
\]

where the reference irradiance is 1,000 W/m² and the reference cell temperature is 25 °C. A temperature difference of one degree Celsius is one kelvin, so the coefficient is represented as K⁻¹ and temperatures are stored as absolute kelvin values in Graphcal.

## Adapted inputs

The 5 kW nameplate rating, coefficient, and four operating points are original illustrative corpus inputs rather than copied weather or system data:

| Period | Effective irradiance (W/m²) | Cell temperature (°C / K) | Duration (h) |
|---|---:|---:|---:|
| Low sun | 200 | 15 / 288.15 | 1 |
| Mid-morning | 600 | 25 / 298.15 | 1 |
| Solar noon | 1,000 | 45 / 318.15 | 1 |
| Afternoon | 400 | 35 / 308.15 | 1 |

Other inputs are \(P_{dc0}=5\) kW, \(\gamma=-0.004\ \text{K}^{-1}\), \(I_{ref}=1000\) W/m², and \(T_{ref}=298.15\) K.

This project starts at transmitted/effective irradiance and supplied cell temperature. It does not reproduce the other PVWatts submodels or calculate AC energy.

## Independent calculation

Applying Equation 8 independently of Graphcal:

| Period | Irradiance factor | Temperature factor | DC power (kW) | DC energy (kWh) |
|---|---:|---:|---:|---:|
| Low sun | 0.2 | \(1+(-0.004)(15-25)=1.04\) | 1.04 | 1.04 |
| Mid-morning | 0.6 | 1.00 | 3.00 | 3.00 |
| Solar noon | 1.0 | \(1+(-0.004)(45-25)=0.92\) | 4.60 | 4.60 |
| Afternoon | 0.4 | \(1+(-0.004)(35-25)=0.96\) | 1.92 | 1.92 |

Therefore:

\[
E_{dc}=1.04+3.00+4.60+1.92=10.56\ \text{kWh}
      =38{,}016{,}000\ \text{J}.
\]

The manifest checks low-sun power (1,040 W), peak power (4,600 W), total energy (38,016,000 J), and the selected display units. The narrow tolerances permit only floating-point evaluation differences.

## Licensing and adaptation

The equation was reimplemented from the cited NREL technical report. No report prose, figures, software, or datasets are reproduced. The operating points, source, and calculation record are original corpus content under the repository license; the report is cited for provenance and is not relicensed here.
