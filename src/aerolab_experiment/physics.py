"""Low-speed, dry-air pitot/static reductions in SI units.

v0.1 assumes an incompressible flow, a correctly aligned pitot-static probe,
properly calibrated force measurements in wind axes, and a rectangular model.
No model support interference, blockage, humidity or buoyancy corrections.
"""
from __future__ import annotations
from math import sqrt, hypot
from .models import Config, Measurement, Result

R_DRY_AIR = 287.05   # J/(kg K), dry-air gas constant
MU0 = 1.716e-5       # Pa s, Sutherland reference value
T0 = 273.15          # K
SUTHERLAND_S = 110.4 # K


def air_density_dry(pressure_pa: float, temp_c: float) -> float:
    """Ideal dry-air density p/(R*T); humidity effects are not included."""
    if pressure_pa <= 0 or temp_c <= -273.15:
        raise ValueError("pressure > 0 and temperature above absolute zero required")
    return pressure_pa / (R_DRY_AIR * (temp_c + 273.15))


def air_viscosity_sutherland(temp_c: float) -> float:
    """Dynamic viscosity of dry air (Pa s) via Sutherland approximation."""
    T = temp_c + 273.15
    if T <= 0:
        raise ValueError("temperature must exceed absolute zero")
    return MU0 * (T / T0) ** 1.5 * (T0 + SUTHERLAND_S) / (T + SUTHERLAND_S)


def reynolds_number(rho: float, velocity_m_s: float, chord_m: float, mu: float) -> float:
    if rho <= 0 or velocity_m_s < 0 or chord_m <= 0 or mu <= 0:
        raise ValueError("Reynolds input outside physical domain")
    return rho * velocity_m_s * chord_m / mu


def analyze_measurement(m: Measurement, cfg: Config) -> Result:
    """One steady-state row, with 1-sigma first-order uncertainty estimates.

    Independent input uncertainties only. Geometry and tare uncertainties shared
    across multiple rows are correlated and NOT reduced by averaging replicates.
    """
    g, tare, u = cfg.geometry, cfg.tare, cfg.uncertainty
    area = g.reference_area_m2
    net_lift = m.lift_N - tare.lift_N
    net_drag = m.drag_N - tare.drag_N
    q = m.dp_pa - tare.dp_pa
    if q <= 0:
        raise ValueError(f"run_id={m.run_id!r}: tare-corrected dynamic pressure must be > 0 Pa, got {q:g}")
    rho = air_density_dry(m.ambient_pressure_pa, m.temp_c)
    mu = air_viscosity_sutherland(m.temp_c)
    vel = sqrt(2.0 * q / rho)
    re = reynolds_number(rho, vel, g.chord_m, mu)
    cl, cd = net_lift / (q * area), net_drag / (q * area)

    # Correct even near zero force (no relative uncertainty division by force).
    u_q = hypot(u.dp_pa, u.dp_tare_pa)
    u_lift = hypot(u.lift_N, u.lift_tare_N)
    u_drag = hypot(u.drag_N, u.drag_tare_N)
    u_area_rel = hypot(u.chord_m / g.chord_m, u.span_m / g.span_m)

    def coefficient_u(net_force: float, u_force: float) -> float:
        return sqrt(
            (u_force / (q * area)) ** 2
            + (net_force * u_q / (q * q * area)) ** 2
            + (net_force * u_area_rel / (q * area)) ** 2
        )

    T = m.temp_c + 273.15
    u_rho_relative = hypot(
        u.ambient_pressure_pa / m.ambient_pressure_pa, u.temp_c / T
    )
    u_vel = vel * 0.5 * hypot(u_q / q, u_rho_relative)

    # Re = chord * sqrt(2*p*q/(R*T)) / mu(T)
    # Direct independent-input derivatives avoid counting shared temperature twice.
    dln_mu_dT = 1.5 / T - 1.0 / (T + SUTHERLAND_S)
    u_re_rel = sqrt(
        (u.chord_m / g.chord_m) ** 2
        + (0.5 * u_q / q) ** 2
        + (0.5 * u.ambient_pressure_pa / m.ambient_pressure_pa) ** 2
        + ((-0.5 / T - dln_mu_dT) * u.temp_c) ** 2
    )
    return Result(
        run_id=m.run_id, alpha_deg=m.alpha_deg,
        lift_net_N=net_lift, drag_net_N=net_drag, q_pa=q,
        density_kg_m3=rho, viscosity_pa_s=mu,
        velocity_m_s=vel, reynolds=re,
        cl=cl, cd=cd, u_cl=coefficient_u(net_lift, u_lift),
        u_cd=coefficient_u(net_drag, u_drag),
        u_velocity_m_s=u_vel, u_reynolds=re * u_re_rel,
    )
