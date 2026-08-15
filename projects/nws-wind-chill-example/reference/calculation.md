# NWS wind-chill source evidence

## Candidate generation

This source-backed candidate was prepared by an AI coding agent at the repository maintainer's direction from the cited public National Weather Service page. It does not derive from private material. Human source, privacy, adaptation, and promotion review remain pull-request responsibilities.

## Source and published expected value

National Weather Service, “Understanding Wind Chill,” https://www.weather.gov/safety/cold-wind-chill-chart, accessed 2026-08-16.

The page publishes the U.S. wind-chill equation

\[
W = 35.74 + 0.6215T - 35.75V^{0.16} + 0.4275TV^{0.16},
\]

where \(T\) is air temperature in degrees Fahrenheit and \(V\) is wind speed in miles per hour. The same page explicitly states that 0 °F air with a 15 mph wind produces a wind chill of −19 °F.

That source-reported −19 °F value—not a locally generated higher-precision result—is the manifest's expected value.

## Adaptation and source-to-assertion mapping

Graphcal has no affine Fahrenheit unit, so the model explicitly names the temperature and output as conventional Fahrenheit numeric values. Wind speed remains a physical `Velocity` and is normalized by an explicitly defined mph before entering the empirical equation.

The source presents the result to a whole degree. The model applies `round`, and the manifest maps the source output as:

- `/node/reported_wind_chill_fahrenheit_value/si_value` = `-19.0`.

The unrounded internal result is intentionally not asserted because the NWS page does not report those extra digits.

The NWS defines wind chill only for temperatures at or below 50 °F and wind speeds above 3 mph. The reproduced inputs are within that domain. This case reproduces one published example and does not make a broader weather-safety claim.

## Licensing and adaptation

Only the published equation and one numerical example are reimplemented. No source prose, chart image, calculator software, or dataset is copied. The Graphcal source and this evidence record are original corpus content under the repository license; the NWS page is cited for provenance and is not relicensed here.
