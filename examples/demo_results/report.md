# AeroLab Experiment Analysis

**Data type:** SYNTHETIC — DEMONSTRATION ONLY; not real measurements.
**Rows:** 27 | **Angle groups:** 9
**Reference area:** 0.02 m²
**Reynolds range:** 4.358e+04–4.47e+04

## Quality checks

- No basic QC warnings; this is NOT experimental validation.

## Measurement model

- Raw force values are **calibrated to newtons, but not yet tare-corrected**.
- Lift/drag are in **wind axes**; convert balance axes upstream if necessary.
- q = dp_raw − dp_tare, using pitot total-minus-static pressure in Pa.
- Reference area = chord × span (rectangular specimen, m²).
- CL = (L_raw − L_tare)/(q A); CD = (D_raw − D_tare)/(q A).
- rho = p/(R T), dry ideal air; mu(T) from Sutherland's law.
- U = sqrt(2q/rho); Re = rho U chord / mu.
- u(CL), u(CD), u(U), u(Re) use first-order independent-input uncertainty propagation (k=1).
- Repeated-angle sample standard deviations and SEM measure scatter **only**; they do not remove shared systematic uncertainties.

## Important limitations

- No actual sensor calibration, calibration certificate, or uncertainty budget has been independently verified.
- No test-section velocity uniformity, turbulence intensity, pitot alignment, wall blockage, support interference, airfoil deformation, hysteresis, or force-frame rotation correction.
- Zero and sign conventions must be validated by the experimenter.
- These are **3D finite-span model coefficients**, not automatically comparable to 2D airfoil polars.
- No proof of agreement with CFD, XFOIL, or literature is implied.

## Provenance

- Input CSV SHA-256: `682de33f5ffbbffba1cb7bd087c0fe55893e050c519f2128e4ade79abb8c3698`
- Configuration SHA-256: `d86b1795bdcc85b7e28136d5955883c51ccc02100e80d937815f24162de0df61`
- AeroLab version: 0.1.0
