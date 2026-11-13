# FAO-24 soil-water-balance source evidence

## Candidate generation

This source-backed candidate was prepared by an AI coding agent at the repository maintainer's direction from the cited public Food and Agriculture Organization publication. It does not derive from private material. Human source, privacy, adaptation, and promotion review remain pull-request responsibilities.

## Source and published expected values

J. Doorenbos and W. O. Pruitt, *Guidelines for Predicting Crop Water Requirements*, FAO Irrigation and Drainage Paper 24, revised 1977, Part II, Section 2.2.1, cotton field-irrigation-schedule example on pages 89–90, https://www.fao.org/4/f2430e/f2430e.pdf, accessed 2026-08-16.

For a March-through-August cotton growing season, the example prints monthly beginning balance (`Wb`), effective rainfall (`Pe`), groundwater contribution (`Ge`), crop evapotranspiration (`ETcotton`), and end balance (`We`). It states

\[
W_e = W_b + G_e + P_e - ET_{crop}.
\]

The reproduced source values are:

| Month | Rainfall (mm) | Groundwater (mm) | ETcrop (mm) | Published end balance (mm) |
|---|---:|---:|---:|---:|
| March | 90 | 0 | 45 | 145 |
| April | 50 | 0 | 110 | 85 |
| May | 20 | 0 | 225 | −120 |
| June | 0 | 0 | 285 | −405 |
| July | 0 | 0 | 280 | −685 |
| August | 0 | 0 | 120 | −805 |

The March beginning balance is 100 mm; each subsequent beginning balance is the preceding printed end balance. Those six FAO-reported end balances—not locally generated extra digits—are the reference expectations.

## Adaptation and source-to-assertion mapping

The `Month` declaration preserves the publication's chronological order. Each `MonthlyWaterAccount` record carries the three monthly terms, and `scan` uses a `Length` accumulator initialized to 100 mm. Its closure destructures each record and applies FAO's printed balance equation. The manifest maps the direct source outputs as:

- `/node/reported_end_of_month_balance/entries/March/display_value` = `145.0`;
- `/node/reported_end_of_month_balance/entries/April/display_value` = `85.0`;
- `/node/reported_end_of_month_balance/entries/May/display_value` = `-120.0`;
- `/node/reported_end_of_month_balance/entries/June/display_value` = `-405.0`;
- `/node/reported_end_of_month_balance/entries/July/display_value` = `-685.0`;
- `/node/reported_end_of_month_balance/entries/August/display_value` = `-805.0`;
- the corresponding entry units are `mm`.

The source prints whole millimetres. A sub-nanometre tolerance covers only binary unit-scaling representation and does not widen those source expectations.

## Graphcal feature coverage

This project intentionally exercises previously uncovered behavior:

- a record-shaped algebraic data type indexed over an ordered named axis;
- constructor payload binding in an exhaustive `match`;
- `scan` over algebraic source elements with a quantity accumulator;
- indexed tolerance assertions and `#[assumes]` metadata;
- element-wise comparison producing `Bool[Month]`, `if`, `sum`, and exact conversion to `Int`;
- `argmin` producing `Key<Month>` and computed-key element access;
- a unit-aware line plot with a boolean color channel.

The deficit count, minimum key, and plot are feature checks only. They are not manifest reference assertions because the publication does not explicitly report those derived summaries.

## Licensing and adaptation

Only the small worked-example table and its balance equation are transcribed. No publication figures, software, or substantial prose are copied. The Graphcal source and this evidence record are original corpus content under the repository license; the FAO publication is cited for provenance and is not relicensed here.
