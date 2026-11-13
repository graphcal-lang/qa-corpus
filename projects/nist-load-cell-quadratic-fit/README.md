# NIST load-cell quadratic fit

This source-backed reproduction asks: **Does a dense quadratic least-squares fit of NIST's 40 load-cell observations reproduce the coefficients and residual standard deviation reported by NIST?**

Unlike the earlier scalar corpus projects, it exercises `Fin` axes, a multi-declaration table, a coordinate axis, conditionals over keys, dense matrix operations (`transpose`, `matmul`, `solve`, `inverse`, and `det`), vector operations (`dot` and `norm`), assertions with assumption metadata, and layered unit-aware plotting.

The source data, coefficient normalization, source precision, and assertion mapping are documented in [`reference/calculation.md`](reference/calculation.md).
