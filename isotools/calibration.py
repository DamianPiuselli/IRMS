"""Calibration module for applying normalization strategies."""

from typing import List
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
        Pass 1: Row-by-row calibration for DIAGNOSTICS (Plots).
        Does NOT calculate combined uncertainty.
        """
        df = raw_df.copy()

        # 1. Isolate and Aggregate Standards for Fitting
        std_names = [s.name for s in standards]
        std_subset = df[df["sample_name"].isin(std_names)]

        if std_subset.empty:
            raise ValueError("No standards found in the input DataFrame.")

        # Aggregate standards to get the points for the curve fit
        std_stats = std_subset.groupby("sample_name")[target_col].agg(["mean", "sem"])
        std_stats["sem"] = std_stats["sem"].fillna(0.0)

        # 2. Fit the Strategy (Calculates Slope/Intercept)
        self.strategy.fit(std_stats, standards)

        # 3. Apply Correction to ALL Rows
        # We only predict the value, we don't propagate uncertainty here
        df["corrected_delta"] = df[target_col].apply(self.strategy.predict)

        return df

    def propagate_uncertainty(
        self, summary_df: pd.DataFrame, target_col: str = "d15n"
    ) -> pd.DataFrame:
        """
        Pass 2: Kragten propagation on AGGREGATED data for REPORTING.

        Args:
            summary_df: The output of Processor.summarize().
                        Must contain '{target_col}_mean' and '{target_col}_sem'.
        """
        df = summary_df.copy()

        # We will calculate the final values and uncertainties
        corrected_values = []
        uncertainties = []

        for _, row in df.iterrows():
            # Extract the Aggregate Raw Statistics
            # e.g., 'd15n_mean' and 'd15n_sem'
            raw_mean = row.get(f"{target_col}_mean")
            raw_sem = row.get(f"{target_col}_sem", 0.0)

            # Perform Kragten Propagation on the MEAN
            # This correctly combines the SEM (precision) with the Calibration Error (trueness)
            corr, unc = self._generic_kragten(raw_mean, raw_sem)

            corrected_values.append(corr)
            uncertainties.append(unc)

        # Overwrite/Add the rigorous columns
        df["corrected_delta_mean"] = corrected_values
        df["combined_uncertainty"] = uncertainties

        return df

    def _generic_kragten(self, val, unc):
        """
        Standard Kragten numerical differentiation.
        val: The Raw Mean of the sample
        unc: The Raw SEM of the sample
        """
        # A. Nominal Calculation
        y0 = self.strategy.predict(val)

        # B. Get Strategy Parameters (Slope, Intercept, Standards values, etc)
        model_params = self.strategy.get_kragten_params()

        sum_squares = 0.0

        # C. Perturb Model Parameters (Systematic Error)
        for i, param in enumerate(model_params):
            _, unc_p = param

            # Create list of nominal values
            current_args = [p[0] for p in model_params]
            # Perturb just this one parameter
            current_args[i] += unc_p

            # Predict using perturbed model
            y_p = self.strategy.predict_perturbed(val, current_args)
            sum_squares += (y_p - y0) ** 2

        # D. Perturb the Sample Itself (Random Error / Precision)
        # We perturb the INPUT value by its SEM
        y_samp_p = self.strategy.predict(val + unc)
        sum_squares += (y_samp_p - y0) ** 2

        return y0, np.sqrt(sum_squares)
