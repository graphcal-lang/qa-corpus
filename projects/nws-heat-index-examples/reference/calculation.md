# NWS heat-index source evidence

## Candidate generation

This source-backed candidate was prepared by an AI coding agent at the repository maintainer's direction from the cited public National Weather Service page. It does not derive from private material. Human source, privacy, adaptation, and promotion review remain pull-request responsibilities.

## Source and published expected values

National Weather Service, Weather Forecast Office Amarillo, “What is the heat index?”, https://www.weather.gov/ama/heatindex, accessed 2026-08-16.

The page publishes the Rothfusz regression

\[
\begin{aligned}
HI={}&-42.379+2.04901523T+10.14333127RH-0.22475541T RH\\
&-0.00683783T^2-0.05481717RH^2+0.00122874T^2RH\\
&+0.00085282T RH^2-0.00000199T^2RH^2,
\end{aligned}
\]

with \(T\) in degrees Fahrenheit, \(RH\) as a percentage, and \(HI\) in degrees Fahrenheit. The same NWS page explicitly reports these examples:

| Example | Source air temperature | Source relative humidity | Source heat index |
|---|---:|---:|---:|
| Humid | 100 °F | 55% | 124 °F |
| Dry | 100 °F | 15% | 96 °F |

Those two source-reported output values—not a locally calculated higher-precision result—are the manifest's expected values.

## Adaptation and source-to-assertion mapping

Graphcal does not define affine Fahrenheit units. The regression itself requires conventional Fahrenheit and percentage numeric values, so the project names and types those inputs explicitly as dimensionless numeric values rather than pretending they are multiplicative temperature quantities. The output is likewise named `*_fahrenheit_value`.

The page presents the examples to whole degrees. Evaluating the published regression gives values near 123.64 and 95.85 before presentation; Graphcal applies `round` and the manifest asserts exactly:

- `/node/humid_example_heat_index_fahrenheit_value/si_value` = `124.0`, from the NWS 100 °F / 55% example;
- `/node/dry_example_heat_index_fahrenheit_value/si_value` = `96.0`, from the NWS 100 °F / 15% example.

The local regression evaluation only connects the model to the published whole-degree examples; it is not the source of the expected values.

The NWS notes that the regression is an approximation with an error of ±1.3 °F and that chart values are for shady locations. This project reproduces the two reported examples only; it does not make a broader heat-safety claim.

## Licensing and adaptation

Only the published equation and two numerical examples are reimplemented. No source prose, chart image, software, or dataset is copied. The Graphcal source and this evidence record are original corpus content under the repository license; the NWS page is cited for provenance and is not relicensed here.
