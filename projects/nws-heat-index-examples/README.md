# NWS heat-index examples

This source-backed reproduction asks: **Does the National Weather Service heat-index regression reproduce two values explicitly reported by NWS for 100 °F air?**

The NWS page publishes the regression and reports heat indexes of 124 °F at 55% relative humidity and 96 °F at 15% relative humidity. The project applies the published regression and rounds to the whole-degree presentation used by the source. The source-to-assertion mapping and the required Fahrenheit adaptation are documented in [`reference/calculation.md`](reference/calculation.md).
