# Roadmap — scientific value before feature count

0.1.0 (implemented): strict ingestion, offsets, SI physics, simple k=1 uncertainty,
repeat-angle scatter, plots, caveated report, SHA-256 reproducibility, synthetic data,
unit tests.

0.1.1 (next): measured calibration datasets, pitot probe alignment check,
uncertainty parameter definitions from real calibration certificates, more edge tests,
CLI `validate`, CLI support for exporting machine-readable QC flags.

0.2: calibration fitting and zero/tare tests (support off/on), wind-axis transform for
normal/axial load cells, robust per-run time-window averaging and run metadata.

0.3: configurable humidity-corrected air properties, uncertainty covariance or
Monte Carlo propagation, repeatability vs reproducibility decomposition.

0.4: import and strictly provenance-tag external polars for comparison at matched Re,
geometry, uncertainty and turbulence conditions. No broad 'validated' label.

0.5: standardized experimental campaign definitions, wall/blockage/support corrections
with applicability checks, benchmarking and user studies.

0.6+: optional Arduino/serial sensor logger and offline dashboard, after hardware
sampling and calibration conventions are documented.

Potential user testing: ask 3-5 student researchers to reduce a dataset with and
without AeroLab and compare traceability, unit errors, and time spent. Pre-register
questions; do not present synthetic demonstration as real validation.
