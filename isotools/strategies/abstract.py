from abc import ABC, abstractmethod
from typing import Dict
import pandas as pd
from isotools.models import ReferenceMaterial


class CalibrationStrategy(ABC):
    """
    Abstract base class for calibration logic.
    """

    @abstractmethod
    def fit(self, anchor_stats: pd.DataFrame, refs: Dict[str, ReferenceMaterial]):
        """
        Calculates model parameters (Slope, Intercept) based on Anchor Standards.

        Args:
            anchor_stats: DataFrame with index=sample_name, columns=['mean', 'sem'].
            refs: Dictionary mapping sample_name -> ReferenceMaterial object.
        """

    @abstractmethod
    def apply(self, df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """
        Applies the calibration to the 'Row-Level' data (vectorized).
        Adds a 'corrected_<target_col>' column.
        """

    @abstractmethod
    def propagate(self, summary_df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """
        Applies Kragten propagation to the 'Sample-Level' aggregated data.
        Returns DataFrame with 'combined_uncertainty'.
        """
