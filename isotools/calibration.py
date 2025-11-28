"""Calibration module implementing various calibration strategies."""

from typing import List
import numpy as np
import pandas as pd
from .schemas import ReferenceMaterial
from .strategies import CalibrationStrategy


class Calibrator:
    def __init__(self, strategy: CalibrationStrategy):
        self.strategy = strategy

    def calibrate(
        self, stats_df: pd.DataFrame, standards: List[ReferenceMaterial]
    ) -> pd.DataFrame:
        """
        Returns the input DataFrame with new columns: 'corrected_delta', 'combined_uncertainty', 'is_standard'.
        """
        # Work on a copy to avoid SettingWithCopy warnings on the original
        df = stats_df.copy()

        # 1. Train
        self.strategy.fit(df, standards)

        # 2. Vectorized prediction (much faster than iterating rows for the nominal value)
        # Note: Depending on your strategy logic, you might keep the loop for Kragten,
        # but apply the results back to the DF columns.

        corrected_list = []
        uncertainty_list = []

        # Iterate over the dataframe using iterrows (safe enough for this scale)
        for _, row in df.iterrows():
            raw_val = row["mean"]
            raw_sem = row.get("sem", 0.0)  # Handle missing SEM safely

            corr, unc = self._generic_kragten(raw_val, raw_sem)
            corrected_list.append(corr)
            uncertainty_list.append(unc)

        # 3. Assign back to DataFrame
        df["corrected_delta"] = corrected_list
        df["combined_uncertainty"] = uncertainty_list

        # 4. Add metadata for convenience (e.g., mark which rows are standards)
        std_names = {s.name: s.true_delta for s in standards}
        df["true_value"] = df.index.map(std_names)  # Assuming index is sample_name
        df["is_standard"] = df["true_value"].notna()
        df["residual"] = df["corrected_delta"] - df["true_value"]

        return df

    def _generic_kragten(self, val, unc):
        """
        This works for ANY strategy (1-point, 2-point, Multi-point).
        It asks the strategy for parameters, then perturbs them blindly.
        Obs:
        unc should be the SEM value of the sample measurements.
        """
        # A. Nominal Calculation
        y0 = self.strategy.predict(val)

        # B. Get Strategy Parameters (e.g., The Standards data)
        model_params = self.strategy.get_kragten_params()

        sum_squares = 0.0

        # C. Perturb Model Parameters (Slope/Intercept influencers)
        # We assume model_params is list of (value, uncertainty)
        for i, param in enumerate(model_params):
            # Create list of nominal values
            current_args = [p[0] for p in model_params]
            # Add uncertainty to i-th parameter
            current_args[i] += param[1]

            # Predict using perturbed model
            y_p = self.strategy.predict_perturbed(val, current_args)
            sum_squares += (y_p - y0) ** 2

        # D. Perturb the Sample Itself (The 'x' term)
        y_samp_p = self.strategy.predict(val + unc)
        sum_squares += (y_samp_p - y0) ** 2

        return y0, np.sqrt(sum_squares)
