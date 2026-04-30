"""
Calibration strategies for IRMS data.
"""
from .abstract import CalibrationStrategy
from .normalization import TwoPointLinear, MultiPointLinear
