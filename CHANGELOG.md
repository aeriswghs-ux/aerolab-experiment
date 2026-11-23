# Changelog

## 0.1.0 — 2026-11-23

- Strict SI CSV + JSON contract for calibrated but untared wind-axis lift/drag forces.
- Dry-air density and Sutherland viscosity; pitot-static velocity and Reynolds calculations.
- Tare-aware CL/CD reduction and first-order k=1 independent-input uncertainty.
- Repeat-angle summary (sample standard deviation and SEM) separately from instrument uncertainty.
- CLI exports CSV, Markdown caveat report, SHA-256 manifest, and optional Matplotlib plots.
- Seeded, conspicuously synthetic demonstration dataset.
- Initial automated numeric, input-validation, and CLI integration tests.

Not implemented: calibration fitting, model-axis rotation, raw ADC ingestion, wall corrections,
uncertainty correlations/covariance, environmental humidity, or unsteady aerodynamics.
# Validation extension (2026-11-23)

- Added attributed, hash-pinned Ladson experimental reference data.
- Added independent numerical/uncertainty verification and mismatch-aware comparisons.
- Added 14 tests (37 total), reproducible scripts, reference plots, and source notices.
- No matched NACA 0018 or physical tunnel validation claimed; core remains v0.1.0.
# Low-Reynolds reference extension (2026-11-23)

- Added UIUC Volume 1 source data with original GPL, provenance and notices.
- Analyzed 67 points in seven runs at Re=40,000–101,600, including rounding and Reynolds-sensitivity checks.
- Documented provisional Re=40,000–100,000 wind-tunnel goals and required nominal speeds.
- Added parser/source tests (40 total); no NACA 0018 physical validation claimed.

