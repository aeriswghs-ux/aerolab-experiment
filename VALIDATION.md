# Verification results and validation limits

**Software verification completed for the tested cases. Physical tunnel validation NOT performed.**

The current intended tunnel target is low Reynolds numbers (provisionally
40,000–100,000), not the earlier NASA example at 6 million. See
[WIND_TUNNEL_GOALS.md](WIND_TUNNEL_GOALS.md) and the new
[low-Reynolds experimental reference analysis](LOW_REYNOLDS_RESULTS.md).
Run `python scripts/low_reynolds.py` for its 67-point analysis, rounding check,
Reynolds-sensitivity comparisons, and nominal design setpoints.

Run from the repository root after `python -m pip install -e ".[plot,test]"`:

```sh
python -m pytest -q
python scripts/validate.py
# Optional: re-fetch and verify the bundled experimental reference
python scripts/fetch_reference.py
```

`validation/results/summary.json` is the detailed machine-readable result; `verification.csv` contains numerical checks. Plots show published reference curves and trip sensitivity, not AeroLab predictions. The package is a data reducer, not an aerodynamic prediction model.

## Independent software checks

The script uses synthetic input row 13 (zero-based index 12), an independently written vector calculation, central differences for all ten uncertain inputs, and 100,000 independent Gaussian Monte Carlo draws with seed 20261123. These distributions and budgets are test assumptions, not measured instrument errors. Acceptance thresholds are 1e-12 relative for values, 1e-6 for finite-difference uncertainties, and 3% for Monte Carlo standard deviations. The latter is a numerical sanity threshold, not a physical validation criterion. One configuration does not establish accuracy for all operating conditions, especially near zero dynamic pressure.

| Quantity | Value | Analytic standard uncertainty, k=1 | Monte Carlo deviation from analytic u |
|---|---:|---:|---:|
| CL | 0.2511930734 | 0.01096383065 | 0.4514% |
| CD | 0.04599092755 | 0.004228077115 | 0.1157% |
| Speed, m/s | 6.733202856 | 0.05611686881 | 0.2107% |
| Reynolds | 43930.17874 | 432.6017043 | 0.1750% |

Maximum relative finite-difference uncertainty discrepancy: 9.77e-11. Maximum coefficient absolute discrepancy: 5.56e-17. The independent code shares the documented physical model and constants, so agreement verifies implementation, not the physical model itself. No reference-polars-to-force round trip is presented as experimental evidence.

## Quantitative experimental reference comparison

Six pre-stall pairs compare 80-grit to nearest 180-grit Ladson rows, selecting 80-grit angles in [-4,10] degrees and using an explicit 0.25-degree tolerance. No interpolation or extrapolation. Both sets are Re=6 million; transition conditions differ and every pair is flagged. Differences include residual angle offsets. This is a **trip sensitivity example, not matched validation**.

| Coefficient | MAE | RMSE | Pairs |
|---|---:|---:|---:|
| CL | 0.008600 | 0.0110943 | 6 |
| CD | 0.000206667 | 0.000304576 | 6 |

Reference standard uncertainty is unavailable in the distributed table. Combined uncertainty and normalized residuals therefore remain null; no confidence intervals or statistical agreement claims are calculated. For known independent k=1 uncertainties the comparator uses sqrt(u_observed^2+u_reference^2). Correlated sources need covariance support before use.

## NACA 0018 mismatch audit

All 27 synthetic demo rows are excluded from matched comparison: NACA 0018 versus NACA 0012, finite-span versus section coefficients, unspecified transition, and Re approximately 43,582–44,697 versus 6,000,000. Angle differences exceeding 0.1 degree are also flagged. Default Re tolerance is 1%; these tolerances are screening choices, not universal physics criteria. Numeric differences remain diagnostic only. Even matching metadata would not turn synthetic rows into physical evidence.

## Remaining work for real tunnel validation

Collect calibrated tunnel measurements, geometry, Reynolds/AoA uncertainty, transition/roughness, flow uniformity, turbulence, support/wall corrections, and repeatability. Select a permitted NACA 0018 reference at compatible conditions. Resolve finite-span/2D differences, Mach, hysteresis, and uncertainty covariance. Angle uncertainty and interpolation uncertainty are not implemented. Metadata matching is necessary but insufficient; the comparator does not check every physical condition or certify validation.

Original baseline: 23/23 tests passed after installation (the initial uninstalled CLI invocation failed). Expanded suite and reproducibility checks are recorded in `validation/results/test-results.txt`. License and source decisions are in DATA_SOURCES.md and THIRD_PARTY_NOTICES.md.
