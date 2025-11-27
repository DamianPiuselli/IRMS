"""Data schemas for isotopic processing results and reference materials."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ReferenceMaterial:
    """
    Immutable definition of a Reference Material (Standard).
    Example: ReferenceMaterial("USGS32", 180.0, 1.0)
    """

    name: str
    true_delta: float  # The certified value (e.g., 180.0)
    uncertainty_1s: float  # Standard uncertainty (1 sigma)

    def __post_init__(self):
        # Basic validation to ensure physics makes sense
        if self.uncertainty_1s < 0:
            raise ValueError(f"Uncertainty for {self.name} cannot be negative.")


@dataclass
class CalculationResult:
    """
    The final output for a single sample after Kragten propagation.
    """

    identifier: str
    raw_mean: float
    corrected_delta: float
    combined_uncertainty: float  # The final 'u_c' from Kragten

    # Optional: You might want to track which standards were used for this result
    calibrated_with: Optional[str] = None  # e.g., "USGS32/USGS34"

    def to_dict(self):
        """Helper to easily convert back to a DataFrame later."""
        return {
            "Identifier": self.identifier,
            "Raw_Mean": self.raw_mean,
            "Corrected_Delta": self.corrected_delta,
            "Uncertainty_1s": self.combined_uncertainty,
            "Calibration_Ref": self.calibrated_with,
        }
