"""Implementing the strategy design pattern for calibration/normalization methods."""

from typing import List, Tuple
from abc import ABC, abstractmethod
import pandas as pd
from .schemas import ReferenceMaterial


class CalibrationStrategy(ABC):
    """
    Abstract base class for any normalization logic (1-point, 2-point, Regression).
    """

    @abstractmethod
    def fit(
        self,
        stats_df: pd.DataFrame,
        standards: List[ReferenceMaterial],
    ):
        """
        Calculates the model parameters (Slope, Intercept, etc.) based on the standards.
        """

    @abstractmethod
    def predict(self, raw_val: float) -> float:
        """
        Applies the correction to a single raw value using the fitted parameters.
        """

    @abstractmethod
    def get_kragten_params(self) -> List[Tuple[float, float]]:
        """
        Returns a flat list of ALL parameters used in the model and their uncertainties.
        Format: [(val1, unc1), (val2, unc2), ...]
        Used for the generalized Kragten loop.
        """

    @abstractmethod
    def predict_perturbed(self, raw_val: float, perturbed_params: List[float]) -> float:
        """
        Predicts a value using a specific set of perturbed parameters (for Kragten).
        The order of perturbed_params must match the order of get_kragten_params.
        """


class TwoPointStrategy(CalibrationStrategy):
    """
    Implements the FIRMS 2-point linear normalization.
    """

    def __init__(self):
        self.params = []  # Will hold [raw1, raw2, true1, true2]

    def fit(
        self,
        stats_df: pd.DataFrame,
        standards: List[ReferenceMaterial],
    ):
        if len(standards) != 2:
            raise ValueError("TwoPointStrategy requires exactly 2 standards.")

        rm1, rm2 = standards[0], standards[1]

        # Extract data (Simplified for brevity)
        r1_mean = stats_df.loc[rm1.name, "mean"]
        r1_sem = stats_df.loc[rm1.name, "sem"]
        r2_mean = stats_df.loc[rm2.name, "mean"]
        r2_sem = stats_df.loc[rm2.name, "sem"]

        # Store parameters for Kragten: (Value, Uncertainty)
        self.params = [
            (r1_mean, r1_sem),  # Param 0: Raw RM1
            (r2_mean, r2_sem),  # Param 1: Raw RM2
            (rm1.true_delta, rm1.uncertainty_1s),  # Param 2: True RM1
            (rm2.true_delta, rm2.uncertainty_1s),  # Param 3: True RM2
        ]

        # Pre-calculate slope/intercept for fast 'predict' usage
        self.slope = (rm1.true_delta - rm2.true_delta) / (r1_mean - r2_mean)
        self.intercept = rm1.true_delta - (self.slope * r1_mean)

    def predict(self, raw_val: float) -> float:
        return (raw_val * self.slope) + self.intercept

    def get_kragten_params(self):
        return self.params

    def predict_perturbed(self, raw_val: float, p: List[float]) -> float:
        # p maps to the order in self.params: [r1, r2, t1, t2]
        r1, r2, t1, t2 = p[0], p[1], p[2], p[3]

        # Re-calculate slope/intercept based on perturbed values
        m = (t1 - t2) / (r1 - r2)
        b = t1 - (m * r1)
        return (raw_val * m) + b


class SinglePointStrategy(CalibrationStrategy):
    """
    Implements 1-point offset normalization (Shift only).
    Formula: True = Raw + (True_Std - Raw_Std)
    """

    def fit(
        self,
        stats_df: pd.DataFrame,
        standards: List[ReferenceMaterial],
    ):
        if len(standards) != 1:
            raise ValueError("SinglePointStrategy requires exactly 1 standard.")

        rm1 = standards[0]
        r1_mean = stats_df.loc[rm1.name, "mean"]
        r1_sem = stats_df.loc[rm1.name, "sem"]

        self.offset = rm1.true_delta - r1_mean

        self.params = [(r1_mean, r1_sem), (rm1.true_delta, rm1.uncertainty_1s)]

    def predict(self, raw_val: float) -> float:
        return raw_val + self.offset

    def get_kragten_params(self):
        return self.params

    def predict_perturbed(self, raw_val: float, p: List[float]) -> float:
        # p: [r1, t1]
        offset = p[1] - p[0]
        return raw_val + offset
