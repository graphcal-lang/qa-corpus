# USNO J2000 time-scale source evidence

## Candidate generation

This source-backed candidate was prepared by an AI coding agent at the repository maintainer's direction from the cited public U.S. Naval Observatory page. It does not derive from private material. Human source, privacy, adaptation, and promotion review remain pull-request responsibilities.

## Source and published expected values

U.S. Naval Observatory, Astronomical Applications Department, “Terrestrial Time (TT),” https://aa.usno.navy.mil/faq/TT, accessed 2026-08-16.

USNO states that:

- TT equals TAI plus exactly 32.184 seconds;
- J2000.0 is `2000 January 1, 12h TT`;
- the same instant is `2000 January 1, 11:59:27.816 TAI`; and
- the same instant is `2000 January 1, 11:58:55.816 UTC`.

Those published equivalent coordinates are the reference expectations.

## Adaptation and source-to-assertion mapping

The model constructs the source coordinate with `epoch<TT>("2000-01-01T12:00:00")`, then converts that instant with `to_tai` and `to_utc`. To retain the published fractional seconds in scalar manifest assertions, it subtracts each converted coordinate from noon in the same scale. The published coordinates are respectively 32.184 seconds and 64.184 seconds before noon.

The manifest maps the source outputs as:

- `/node/reported_tai_time_before_noon/display_value` = `32.184` s;
- `/node/reported_utc_time_before_noon/display_value` = `64.184` s;
- TAI extractors report hour `11`, minute `59`, and second `27`;
- UTC extractors report hour `11`, minute `58`, and second `55`;
- the two duration `/unit` values are `s`.

The millisecond reporting nodes preserve exactly the source's printed precision. Narrow tolerances cover binary representation only.

## Graphcal feature coverage

This project intentionally exercises previously uncovered behavior:

- `Datetime<TT>`, `Datetime<TAI>`, and `Datetime<UTC>`;
- a constrained datetime input with same-scale constant bounds;
- `epoch<S>`, `to_tai`, `to_utc`, and `to_tt`;
- same-scale datetime subtraction and cross-scale conversion before equality;
- `hour`, `minute`, `second`, `day_of_year`, and `weekday` returning `Int`;
- compound boolean assertions over integers and an exact scale round trip.

Day-of-year and weekday are exercised but not reference assertions because the cited page does not print them.

## Licensing and adaptation

Only public factual time coordinates and scale relationships are reimplemented. No USNO software, page layout, or substantial prose is copied. The Graphcal source and this evidence record are original corpus content under the repository license; the USNO page is cited for provenance and is not relicensed here.
