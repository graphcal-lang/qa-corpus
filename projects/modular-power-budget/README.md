# Modular power budget

This original synthetic project asks: **What source power should be sized for two spacecraft-like electrical loads after conversion losses and design reserve?**

The load declarations live in a separate Graphcal module and are projected through an `include`. The entrypoint sums the loads, accounts for conversion efficiency, and applies a reserve factor. Its checked-in evaluation output is a stability baseline for module resolution, output projection, units, and semantic JSON shape; it is not independent evidence that the sizing assumptions are appropriate for a real system.

Producing revisions, exact semantic comparison rules, and repeated-run determinism are documented in [`reference/baseline.md`](reference/baseline.md).
