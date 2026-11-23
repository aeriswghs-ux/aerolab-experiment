"""Validated, explicit SI input types for experimental data reduction."""

from __future__ import annotations
from dataclasses import dataclass, asdict
from math import isfinite
from typing import Any


def _finite(value: float, field: str, *, positive: bool = False, nonnegative: bool = False) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{field} must be a finite number")
    if positive and value <= 0:
        raise ValueError(f"{field} must be > 0")
    if nonnegative and value < 0:
        raise ValueError(f"{field} must be >= 0")


@dataclass(frozen=True)
class Geometry:
    chord_m: float
    span_m: float

    def __post_init__(self):
        _finite(self.chord_m, "chord_m", positive=True)
        _finite(self.span_m, "span_m", positive=True)

    @property
    def reference_area_m2(self) -> float:
        """Planform reference area for rectangular constant-chord specimen."""
        return self.chord_m * self.span_m


@dataclass(frozen=True)
class Tare:
    lift_N: float
    drag_N: float
    dp_pa: float

    def __post_init__(self):
        for k, v in asdict(self).items():
            _finite(v, f"tare.{k}")


@dataclass(frozen=True)
class Uncertainty:
    """1-sigma standard uncertainties, SI, independent INPUT estimates only.

    Includes repeatability of a *single recorded measurement*, not repeated-angle
    scatter. Shared tare/geometry errors must not be assumed to vanish on averaging.
    """
    lift_N: float
    drag_N: float
    dp_pa: float
    lift_tare_N: float
    drag_tare_N: float
    dp_tare_pa: float
    chord_m: float
    span_m: float
    temp_c: float
    ambient_pressure_pa: float

    def __post_init__(self):
        for k, v in asdict(self).items():
            _finite(v, f"uncertainty.{k}", nonnegative=True)


@dataclass(frozen=True)
class Config:
    geometry: Geometry
    tare: Tare
    uncertainty: Uncertainty
    dataset_kind: str
    forces_frame: str
    dp_source: str

    def __post_init__(self):
        if self.dataset_kind not in {"synthetic", "experimental"}:
            raise ValueError("dataset_kind must be 'synthetic' or 'experimental'")
        if self.forces_frame != "wind_axes":
            raise ValueError("forces_frame must be 'wind_axes'; convert model axes before analysis")
        if self.dp_source != "pitot_total_minus_static":
            raise ValueError("dp_source must be 'pitot_total_minus_static'; do not use ambient pressure as dp")

    @classmethod
    def from_mapping(cls, obj: dict[str, Any]) -> "Config":
        """Reject partial/unknown schemas to avoid silent use of wrong assumptions."""
        expected = {"geometry", "tare", "uncertainty", "dataset_kind", "forces_frame", "dp_source"}
        if set(obj) != expected:
            raise ValueError(f"config keys must be {sorted(expected)}; got {sorted(obj)}")
        if not all(isinstance(obj[k], dict) for k in ("geometry", "tare", "uncertainty")):
            raise ValueError("geometry, tare, and uncertainty must be JSON objects")
        try:
            return cls(
                Geometry(**obj["geometry"]), Tare(**obj["tare"]),
                Uncertainty(**obj["uncertainty"]), obj["dataset_kind"],
                obj["forces_frame"], obj["dp_source"]
            )
        except TypeError as exc:
            raise ValueError(f"config schema error: {exc}") from exc


@dataclass(frozen=True)
class Measurement:
    run_id: str
    alpha_deg: float
    lift_N: float
    drag_N: float
    dp_pa: float
    temp_c: float
    ambient_pressure_pa: float

    def __post_init__(self):
        if not self.run_id or not self.run_id.strip():
            raise ValueError("run_id must be nonempty")
        for name in ("alpha_deg", "lift_N", "drag_N", "dp_pa", "temp_c", "ambient_pressure_pa"):
            _finite(getattr(self, name), name)
        if self.temp_c <= -273.15:
            raise ValueError("temp_c must exceed absolute zero")
        if self.ambient_pressure_pa <= 0:
            raise ValueError("ambient_pressure_pa must be > 0")


@dataclass(frozen=True)
class Result:
    run_id: str
    alpha_deg: float
    lift_net_N: float
    drag_net_N: float
    q_pa: float
    density_kg_m3: float
    viscosity_pa_s: float
    velocity_m_s: float
    reynolds: float
    cl: float
    cd: float
    u_cl: float
    u_cd: float
    u_velocity_m_s: float
    u_reynolds: float
