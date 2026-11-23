"""AeroLab Experiment: small wind-tunnel data reduction, not a CFD solver."""

from .physics import (
    air_density_dry,
    air_viscosity_sutherland,
    analyze_measurement,
    reynolds_number,
)
from .models import Config, Geometry, Tare, Uncertainty, Measurement, Result

__all__ = [
    "air_density_dry", "air_viscosity_sutherland", "analyze_measurement",
    "reynolds_number", "Config", "Geometry", "Tare", "Uncertainty", "Measurement", "Result",
]
__version__ = "0.1.0"
