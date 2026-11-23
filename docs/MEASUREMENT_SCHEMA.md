# Input contract, uncertainties, and interpretive caveats

Required CSV columns (EXACT names, SI units):
- `run_id`: unique nonempty identifier for one **independent steady-state observation**
- `alpha_deg`: signed geometric angle of attack, degrees
- `lift_N`: calibrated lift force in wind axes, N, **before** subtraction of lift tare
- `drag_N`: calibrated drag force in wind axes, N, **before** subtraction of drag tare
- `dp_pa`: pitot total-minus-static differential pressure, Pa, **before** DP tare
- `temp_c`: static ambient air temperature, degrees Celsius
- `ambient_pressure_pa`: absolute ambient pressure, Pa (NOT differential pressure)

Averaging individual samples from one continuous run does NOT automatically make
multiple independent replicates. v0.1 expects one independently identified steady-state
observation per row and exact matching alpha values for group statistics.

JSON config requires geometry {chord_m, span_m}, tare {lift_N, drag_N, dp_pa},
uncertainty {lift_N, drag_N, dp_pa, lift_tare_N, drag_tare_N, dp_tare_pa,
chord_m, span_m, temp_c, ambient_pressure_pa}, dataset_kind ("experimental" or
"synthetic"), forces_frame "wind_axes", and dp_source "pitot_total_minus_static".

Uncertainty keys are standard 1-sigma standard uncertainties, NOT default zeros or
accuracy specifications assumed to equal 1-sigma. Use calibrated uncertainty
budgets, including resolution, noise, drift, calibration, alignment, and bias
where appropriate. If unknown, do not claim final confidence from reported
numbers. Some systematic errors are not captured by this early model.

Force tare, DP tare and geometry uncertainties are shared among rows; their effects
remain correlated across repeats. Reported per-run `u_cl` and `u_cd` include those
components, but summary `cl_sem` and `cd_sem` reflect ONLY between-row scatter.
They must not be combined blindly as independent terms or regarded as total
uncertainty of the group mean.

Reference area is chord*span for a straight rectangular specimen; no automatic
2D comparison or aspect-ratio correction. Lift/drag must already be resolved in
wind axes; normal/axial force balance readings cannot be plugged in as-is.

Equations:
- T = temp_c + 273.15 K, rho = p/(287.05*T)
- mu = 1.716e-5*(T/273.15)^1.5*(273.15+110.4)/(T+110.4) Pa*s
- q = dp - dp_tare; U = sqrt(2q/rho)
- A = chord*span; CL = (lift - tare_lift)/(q*A); CD = (drag - tare_drag)/(q*A)
- Re = rho*U*chord/mu

The ideal-gas, dry-air and low-speed assumptions become inappropriate in conditions
outside these models; automatically estimating compressibility limits is not yet supported.

Important future work: input covariance, pressure tap distribution, geometry and model
axis transformations, nonuniformity and blockage corrections, load-cell calibration,
raw sensor ingestion, humidity and temperature corrections, model support tare,
bootstrapping and hierarchical random-effects statistics.
