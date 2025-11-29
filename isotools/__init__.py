"""
isotools - A library for automated IRMS data processing.
"""

# 1. The Core Controller
# The user's primary starting point.
from .core import Batch

# 2. Data Models
# Necessary for defining new standards or understanding the data structure.
from .models import ReferenceMaterial

# 3. Configurations
# Pre-defined system setups.
from .config import SystemConfig, Nitrogen

# 4. Standards
# The database of known reference materials.
from .standards import USGS32, USGS34, USGS35, get_standard

# 5. Strategies
# The calibration logic needed for Batch.process()
# (Assuming these are exported in isotools/strategies/__init__.py)
from .strategies import CalibrationStrategy, TwoPointLinear

# Define what gets imported with `from isotools import *`
__all__ = [
    "Batch",
    "ReferenceMaterial",
    "SystemConfig",
    "Nitrogen",
    "USGS32",
    "USGS34",
    "USGS35",
    "get_standard",
    "CalibrationStrategy",
    "TwoPointLinear",
]
