# Intended low-Reynolds-number wind-tunnel target

Updated November 23, 2026.

**The intended goal is a small wind tunnel for reproducible low-Reynolds-number airfoil experiments, initially focused on NACA 0018. A provisional planning range is Re=40,000–100,000, with commissioning near Re=40,000–50,000 and later reference runs near 60,000 and 100,000 if calibration and hardware permit. This is a design goal, not a demonstrated operating envelope.**

The user requested a low-Reynolds focus. The numerical range is a planning choice based on the synthetic demo near Re=44,000 and accessible low-Re reference cases; it is not an independently supplied hardware specification. The demo's chord is 100 mm and span 200 mm. Actual model dimensions and test-section capacity must be measured before adopting these setpoints.

## Required conditions for the example 100 mm chord

Calculated using dry air at 20 °C, 101325 Pa, ideal-gas density, and Sutherland viscosity. Speed is Re*mu/(rho*chord). These are nominal design calculations without a measured uncertainty budget.

| Target Re | Required speed (m/s) | Dynamic pressure (Pa) | Status |
|---:|---:|---:|---|
| 40,000 | 6.02 | 21.85 | Initial target |
| 50,000 | 7.53 | 34.13 | Initial target |
| 60,000 | 9.04 | 49.15 | Reference-test goal |
| 100,000 | 15.06 | 136.54 | Extension goal, hardware dependent |

Changing chord or air conditions changes these values. Fan rating alone does not establish test-section speed, uniformity, turbulence or usable force resolution.

## What the new reference results support

UIUC experimental datasets now cover Re=40,000–101,600 for A18, E387 (A), and NACA 64A010. **A18 is not NACA 0018.** These establish useful low-Re data-processing examples and possible future benchmark-model choices. They do not predict NACA 0018 forces or validate our tunnel. Published results and the full comparison methodology are in [LOW_REYNOLDS_RESULTS.md](LOW_REYNOLDS_RESULTS.md).

## Completion criteria for the physical goal

1. Measure actual geometry, calibrated test-section velocity and air conditions; report achieved Re and its uncertainty for each run.
2. Establish force/pressure tare, calibration, drift, repeatability, AoA accuracy, flow uniformity and turbulence; characterize wall/support effects and finite-span differences.
3. Collect real increasing/decreasing AoA sweeps, initially over a conservative range such as -4° to +10°, refining near observed separation or hysteresis. This proposed range is not a claim about stall angle.
4. Compare against a permitted reference with the same airfoil and compatible Reynolds number, transition, geometry, corrections and AoA. If using UIUC references, build the corresponding benchmark model; retain NACA 0018 as the primary research model.
5. Report residuals with a defensible uncertainty budget. Do not widen matching tolerances merely to produce an apparent pass.

No completion deadline or achieved performance is asserted. No actual tunnel measurements have yet been provided to this repository.
