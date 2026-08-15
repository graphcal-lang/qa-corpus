# USNO J2000 time scales

This source-backed reproduction asks: **Does Graphcal convert the U.S. Naval Observatory's J2000.0 Terrestrial Time coordinate to the equivalent TAI and UTC coordinates published by USNO?**

It expands the corpus into constrained `Datetime<S>` values, explicit TT/TAI/UTC conversion, duration arithmetic, millisecond reporting, integer calendar extraction, datetime equality, and boolean assertions.

The time-scale interpretation and source-to-assertion mapping are documented in [`reference/calculation.md`](reference/calculation.md).
