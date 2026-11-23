# v0.1.0 local release audit — 2026-11-23

## Verification performed

- Built as an editable Python package with setuptools locally (no network build dependencies).
- Successfully executed `aerolab --version` (`aerolab-experiment 0.1.0`).
- Unit/integration tests cover physical definitions, tares, errors, config integrity,
  numeric finite-difference agreement of analytic uncertainty derivatives,
  repeatability grouping, CLI outputs, plotting and provenance generation.
- End-to-end CLI reduced 27 **SYNTHETIC** measurements at 9 angles; plotted results.
- No raw physical data, real airfoil polar reference, sensor calibration, uncertainty
  certificate, wall correction, or independent experimental validation was assessed.

## Remaining gaps before scientifically defensible use

1. Obtain genuine measurements, force and pressure calibration constants, and measured
   uncertainty components (with origins).
2. Clarify whether force channels are already resolved into wind axes for every alpha.
3. Determine whether model/support tares vary with angle and modify v0.1 if so.
4. Characterize tunnel velocity uniformity, turbulence and interference.
5. Separate random run-to-run variability from correlated systematic errors across
   repeated angles; v0.1's SEM is **not** an overall uncertainty of the mean.
6. Match reference datasets by Reynolds number, model geometry and tunnel conditions.
7. Conduct third-party user testing and API/API schema design review.

Do not use graphs generated from the bundled example as measured research results.
