"""Data schemas for isotopic processing results and reference materials."""

from dataclasses import dataclass


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

    def __repr__(self) -> str:
        """
        Example: <RefMat USGS32: 180.00 ± 1.00>
        """
        return (
            f"<RefMat {self.name}: "
            f"{self.true_delta:.2f} \u00b1 {self.uncertainty_1s:.2f}\u2030>"
        )
