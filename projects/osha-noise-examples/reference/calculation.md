# OSHA noise-example source evidence

## Candidate generation

This source-backed candidate was prepared by an AI coding agent at the repository maintainer's direction from the cited public Occupational Safety and Health Administration manual. It does not derive from private material. Human source, privacy, adaptation, and promotion review remain pull-request responsibilities.

## Source and published expected values

Occupational Safety and Health Administration, *OSHA Technical Manual*, Section III, Chapter 5, “Noise,” Appendix B.6 and B.8, https://www.osha.gov/otm/section-3-health-hazards/chapter-5, accessed 2026-08-16.

Appendix B.6 publishes the free-field distance equation

\[
L_{p,d2}=L_{p,d1}+20\log_{10}(d_1/d_2).
\]

Its worked aircraft-engine example gives \(L_{p,d1}=120\) dBA at \(d_1=50\) ft and asks for the level at \(d_2=80\) ft. OSHA reports the result as 116 dBA.

Appendix B.8 publishes the eight-hour dose conversion

\[
TWA=16.61\log_{10}(D/100)+90.
\]

Its worked example uses \(D=183\%\) and reports an eight-hour TWA of 94.4 dBA.

Those source-reported 116 dBA and 94.4 dBA values—not locally generated higher-precision results—are the manifest's expected values.

## Adaptation and source-to-assertion mapping

A-weighted decibels are logarithmic levels, not multiplicative physical quantities, so the project names them explicitly as dimensionless dBA numeric values. Distances retain the physical `Length` type and cancel to the dimensionless ratio required by the logarithm.

The model rounds each output to the precision printed by OSHA. The manifest maps the source outputs as:

- `/node/reported_target_sound_level_dba_value/si_value` = `116.0`, from Appendix B.6;
- `/node/reported_eight_hour_twa_dba_value/si_value` = `94.4`, from Appendix B.8.

A narrow tolerance on 94.4 covers only binary representation of the reported decimal; it does not assert unreported precision.

The distance equation assumes a point source in a free field without walls or obstructions, exactly as stated for the source example. This project does not generalize the result to reflective workplaces or non-point sources.

## Licensing and adaptation

Only two published equations and their small worked examples are reimplemented. No source prose, figures, software, or substantial table is copied. The Graphcal source and this evidence record are original corpus content under the repository license; the OSHA page is cited for provenance and is not relicensed here.
