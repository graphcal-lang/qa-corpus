# NASA ideal rocket equation worked example

## Candidate generation

This source-backed candidate was prepared by an AI coding agent at the repository maintainer's direction. The agent reimplemented the cited public worked example in Graphcal; it does not derive from a private project. Human source, privacy, calculation, and promotion review remain pull-request responsibilities.

## Published source and expected result

NASA Glenn Research Center, “Ideal Rocket Equation,” *Beginner's Guide to Aeronautics*, https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/ideal-rocket-equation/, accessed 2026-08-23.

NASA gives the inverse ideal rocket equation

\[
MR = e^{\Delta u/(I_{sp}g_0)}.
\]

Its worked example uses these rounded values:

- specific impulse: about 350 s;
- required velocity increment: about 17,000 mph, also stated as approximately 25,000 ft/s; and
- Earth gravitational acceleration: 32.2 ft/s².

For those values, NASA reports the expected mass ratio directly as \(MR=10\). It also describes the corresponding rocket weight as 90% propellant. The manifest's expected value therefore comes from the published example rather than from Graphcal or a separately generated numerical oracle.

## Reproduction and tolerance

The Graphcal reproduction uses the source's 25,000 ft/s representation and evaluates

\[
MR = e^{25000/(350\times32.2)} \approx 9.1915.
\]

The difference from 10 is expected because NASA labels the input velocities approximate and reports a coarsely rounded result. The manifest consequently compares the calculated mass ratio with NASA's published value of 10 using an absolute tolerance of 1.0. This assertion checks reproduction of the published example at its stated precision; it is not a high-precision numerical oracle.

The local `ft` unit uses the international-foot definition, exactly 0.3048 m, documented by NIST: “U.S. Survey Foot,” https://www.nist.gov/pml/us-surveyfoot, accessed 2026-08-23. Its scale cancels from the dimensionless ratio because both velocity and acceleration use feet.

The analysis is ideal: it neglects gravity loss during the burn, aerodynamic forces, steering loss, staging, and residual propellant, consistent with the cited NASA treatment.

## Licensing and adaptation

The formulas and worked-example values were reimplemented from the cited NASA educational page; no source prose, figures, or tabular data are reproduced. This repository's source and evidence record are original text under the repository license. The cited pages are referenced for provenance and are not relicensed here.
