# AeroLab Python v0.1.0 · aerolab-experiment

A **small, offline-first, measurement-first** wind-tunnel data reduction tool.
It converts *calibrated but untared* wind-axis forces and pitot/static differential
pressure from CSV into CL, CD, Reynolds number, uncertainty estimates and plots.

> **Scientific status: prototype.** The shipped dataset is entirely **SYNTHETIC**.
> Results from the sample are demonstrations of arithmetic, not a validated
> NACA 0018 polar or measurements from any tunnel. There is no CFD solver.

## Reproducible verification and reference data

The validation extension adds independent formula/uncertainty checks, a pinned
NASA Ladson NACA 0012 experimental table, explicit Reynolds/AoA and metadata
mismatch flags, and labeled reference plots. **No physical tunnel validation is
claimed.** The original NACA 0018 demo is synthetic and mismatched to the reference.

```sh
python -m pip install -e ".[plot,test]"
python -m pytest -q
python scripts/validate.py
```

Read [VALIDATION.md](VALIDATION.md) for quantitative results and limits,
[DATA_SOURCES.md](DATA_SOURCES.md) for provenance, and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for attribution.
Generated outputs are in [validation/results](validation/results).
This extension retains the original v0.1.0 core version; it is not a PyPI release.

## Quick start

Python 3.10+ required. From the repository root:

```bash
python -m pip install -e ".[plot]"
python scripts/generate_synthetic.py
python -m aerolab_experiment analyze examples/naca0018_SYNTHETIC.csv --config examples/config.synthetic.json --out outputs/demo --plots
python -m pytest -q  # install pytest first if necessary
```

Or after installation, use the `aerolab` command instead of `python -m aerolab_experiment`.
For CLI/data reduction without plots, plain `pip install -e .` has **zero runtime dependencies**.
The plots extra requires Matplotlib; tests use `pytest` or compatible unittest runner.

Outputs:
- `outputs/demo/analyzed.csv`: per-run coefficients, physics and 1-sigma uncertainty
- `outputs/demo/polar_summary.csv`: repeated-angle means, sample SD and SEM
- `outputs/demo/report.md`: assumptions, warnings and limitations
- `outputs/demo/manifest.json`: input/config SHA-256, version and data type
- `outputs/demo/*.png`: CL/alpha, CD/alpha and drag polar if `--plots`

## Data schema — no implicit guessing

CSV columns are *exactly*:

```csv
run_id,alpha_deg,lift_N,drag_N,dp_pa,temp_c,ambient_pressure_pa
```

- `run_id`: unique ID for one independent steady-state measurement
- `alpha_deg`: degrees, signed
- `lift_N`, `drag_N`: sensor-calibrated forces (in N), **wind axes**, before tare
- `dp_pa`: measured pitot total minus static differential pressure (Pa), before tare
- `temp_c`: static ambient temperature (°C)
- `ambient_pressure_pa`: absolute ambient pressure (Pa) — **not** `dp_pa`

The example configuration defines rectangular area (`chord_m*span_m`), force and
pressure tares, positive uncertainty budgets and explicit assumptions.
For real data, **copy** the JSON, replace it with actual calibration values and
standard uncertainties, and set `dataset_kind` to `experimental`. Never change
that setting for a synthetic demonstration. Details: [measurement schema](docs/MEASUREMENT_SCHEMA.md).

## What this does—and does not—mean

- Assumes calibrated wind-axis lift and drag measurements (not raw HX711 readings).
- Assumes low-speed pitot-static q, dry ideal air, and rectangular planform area.
- Zero and sign conventions must be tested on your hardware.
- Reports first-order standard uncertainty (k=1), assuming independent input
  uncertainty estimates for a **single run**.
- Tare and geometry uncertainty components **do not disappear** with repeated runs;
  group standard deviation / SEM are reported separately.
- No wall/blockage, support interference, angle uncertainty, humidity,
  unsteady-force, pitching-inertia, or 2D section correction in v0.1.
- There is no basis to call any experimental polar "validated" without independent
  calibration, controls, checks, repeats, and appropriate references.

## Development

```bash
python -m pip install -e ".[plot,test]"
pytest -q
```

The code has no cloud or API dependencies, and does not collect user data.
See [research gap](docs/RESEARCH_GAP.md), [calibration checklist](docs/CALIBRATION_CHECKLIST.md), [roadmap](docs/ROADMAP.md),
[measurement model](docs/MEASUREMENT_SCHEMA.md), and [changelog](CHANGELOG.md).

## Sources for the physical definitions

- NASA Glenn, [lift coefficient](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-coefficient/)
- NASA Glenn, [drag coefficient](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-coefficient/)
- NASA Glenn, [dynamic pressure](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/dynamic-pressure/)
- NIST, [law of propagation of uncertainty](https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-appendix-law-propagation-uncertainty)
- Embry-Riddle, [wind tunnel data reduction caveats](https://eaglepubs.erau.edu/introductiontoaerospaceflightvehicles/chapter/wind-tunnel-testing/)

## License
MIT. Contribution and author attribution should reflect the actual work performed.
