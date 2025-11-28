"""Calibration module for applying normalization strategies to raw data."""

from typing import List, Optional
import pandas as pd
import numpy as np
from .schemas import ReferenceMaterial
from .strategies import CalibrationStrategy


class Calibrator:
    def __init__(self, strategy: CalibrationStrategy):
        self.strategy = strategy

    def calibrate(
        self,
        raw_df: pd.DataFrame,
        standards: List[ReferenceMaterial],
        target_col: str = "d15n",
    ) -> pd.DataFrame:
        """
        Calibrates raw data row-by-row.

        1. Aggregates the standard reference materials from the raw data.
        2. Fits the CalibrationStrategy.
        3. Predicts corrected values for every row in the dataframe.

        Returns:
            A new DataFrame with an added 'corrected_delta' column.
        """
        df = raw_df.copy()

        # 1. Isolate and Aggregate Standards for Fitting
        std_names = [s.name for s in standards]
        std_subset = df[df["sample_name"].isin(std_names)]

        if std_subset.empty:
            raise ValueError("No standards found in the input DataFrame.")

        # We need Mean/SEM of standards to fit the strategy
        std_stats = std_subset.groupby("sample_name")[target_col].agg(["mean", "sem"])

        # Handle n=1 (NaN SEM) for standards
        std_stats["sem"] = std_stats["sem"].fillna(0.0)

        # 2. Train the Strategy
        self.strategy.fit(std_stats, standards)

        # 3. Apply Correction to ALL Rows (Vectorized)
        # Note: Strategy.predict works on floats, so we apply it element-wise or vectorized
        # Using lambda for safety with complex strategies, though vectorization is preferred if possible
        df["corrected_delta"] = df[target_col].apply(self.strategy.predict)

        return df
