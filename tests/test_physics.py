import math
import pytest

from aerolab_experiment.models import Config, Geometry, Tare, Uncertainty, Measurement
from aerolab_experiment.physics import (
    air_density_dry, air_viscosity_sutherland, reynolds_number, analyze_measurement,
)


def cfg(**kwargs):
    u = Uncertainty(
        lift_N=.005, drag_N=.002, dp_pa=.4, lift_tare_N=.002,
        drag_tare_N=.001, dp_tare_pa=.2, chord_m=.0005,
        span_m=.001, temp_c=.4, ambient_pressure_pa=100,
    )
    return Config(Geometry(.1, .2), Tare(.012, .006, .3), u,
                  "synthetic", "wind_axes", "pitot_total_minus_static")


def sample(**updates):
    values = dict(run_id="test", alpha_deg=3, lift_N=.212, drag_N=.036,
                  dp_pa=27.3, temp_c=20.0, ambient_pressure_pa=101325.0)
    values.update(updates)
    return Measurement(**values)


def test_standard_air_rho():
    assert air_density_dry(101325, 15) == pytest.approx(1.2250, rel=.001)


def test_sutherland_at_reference():
    assert air_viscosity_sutherland(0) == pytest.approx(1.716e-5)


def test_expected_coefficient_and_reynolds():
    output = analyze_measurement(sample(), cfg())
    assert output.q_pa == pytest.approx(27)
    assert output.lift_net_N == pytest.approx(.2)
    assert output.drag_net_N == pytest.approx(.03)
    assert output.cl == pytest.approx(.2 / (.02 * 27))
    assert output.cd == pytest.approx(.03 / (.02 * 27))
    assert output.reynolds == pytest.approx(
        output.density_kg_m3 * output.velocity_m_s * .1 / output.viscosity_pa_s
    )
    assert output.u_cl > 0 and output.u_cd > 0 and output.u_reynolds > 0


def test_zero_lift_uncertainty_is_finite_nonzero():
    output = analyze_measurement(sample(lift_N=.012), cfg())
    assert output.cl == pytest.approx(0)
    assert output.u_cl == pytest.approx(math.hypot(.005, .002) / (.02 * 27))


def test_zero_all_uncertainty_yields_zero_results():
    zeros = Uncertainty(**{field: 0 for field in Uncertainty.__dataclass_fields__})
    c = cfg()
    c0 = Config(c.geometry, c.tare, zeros, c.dataset_kind, c.forces_frame, c.dp_source)
    out = analyze_measurement(sample(), c0)
    assert out.u_cl == out.u_cd == out.u_velocity_m_s == out.u_reynolds == 0


def test_only_pressure_uncertainty_increases_re_half_relative():
    vals = {field: 0 for field in Uncertainty.__dataclass_fields__}
    vals["ambient_pressure_pa"] = 300
    c = cfg()
    c = Config(c.geometry, c.tare, Uncertainty(**vals), c.dataset_kind, c.forces_frame, c.dp_source)
    out = analyze_measurement(sample(), c)
    assert out.u_reynolds / out.reynolds == pytest.approx(.5 * 300 / 101325)
    assert out.u_cl == out.u_cd == 0


def test_tare_corrected_q_nonpositive_rejected():
    with pytest.raises(ValueError, match="dynamic pressure"):
        analyze_measurement(sample(dp_pa=.1), cfg())


def test_negative_uncertainty_rejected():
    params = {k: 0 for k in Uncertainty.__dataclass_fields__}
    params["drag_N"] = -0.5
    with pytest.raises(ValueError, match="drag_N"):
        Uncertainty(**params)


def test_invalid_temperature_rejected():
    with pytest.raises(ValueError, match="absolute zero"):
        sample(temp_c=-273.15)


def test_force_axis_assumption_is_enforced():
    c = cfg()
    with pytest.raises(ValueError, match="wind_axes"):
        Config(c.geometry, c.tare, c.uncertainty, "synthetic", "body_axes", c.dp_source)


def test_hand_calculated_cl_uncertainty_matches_formula():
    result = analyze_measurement(sample(), cfg())
    q, a, F = 27, .02, .2
    uF = math.hypot(.005, .002)
    uq = math.hypot(.4, .2)
    uArel = math.hypot(.0005/.1, .001/.2)
    ucl = math.sqrt((uF/(q*a))**2 + (F*uq/(q*q*a))**2 + (F*uArel/(q*a))**2)
    assert result.u_cl == pytest.approx(ucl)


def test_incorrect_reynolds_inputs_rejected():
    with pytest.raises(ValueError):
        reynolds_number(1.2, -1, .1, 1e-5)


def test_reynolds_temperature_sensitivity_matches_finite_difference():
    # Verifies analytic u(Re) temperature derivative against a numerical derivative.
    params = {k: 0 for k in Uncertainty.__dataclass_fields__}
    params["temp_c"] = 0.2
    c0 = cfg()
    c = Config(c0.geometry, c0.tare, Uncertainty(**params),
               c0.dataset_kind, c0.forces_frame, c0.dp_source)
    m = sample()
    out = analyze_measurement(m, c)
    h = 1.e-4
    upper = analyze_measurement(sample(temp_c=m.temp_c + h), c).reynolds
    lower = analyze_measurement(sample(temp_c=m.temp_c - h), c).reynolds
    numerical = abs((upper - lower) / (2 * h) * .2)
    assert out.u_reynolds == pytest.approx(numerical, rel=1e-7)


def test_coefficient_uncertainty_matches_numerical_pressure_derivative():
    params = {k: 0 for k in Uncertainty.__dataclass_fields__}
    params["dp_pa"] = 0.35
    c0 = cfg()
    c = Config(c0.geometry, c0.tare, Uncertainty(**params),
               c0.dataset_kind, c0.forces_frame, c0.dp_source)
    out = analyze_measurement(sample(), c)
    h = 1e-4
    upper = analyze_measurement(sample(dp_pa=27.3+h), c).cl
    lower = analyze_measurement(sample(dp_pa=27.3-h), c).cl
    numerical = abs((upper - lower) / (2*h) * .35)
    assert out.u_cl == pytest.approx(numerical, rel=1e-7)
