"""Calibration module implementing various calibration strategies."""

from typing import List
import numpy as np
import pandas as pd
from .schemas import ReferenceMaterial, CalculationResult
from .strategies import CalibrationStrategy


class Calibrator:
    def __init__(self, strategy: CalibrationStrategy):
        self.strategy = strategy

    def calibrate(self, stats_df, standards: List[ReferenceMaterial]):

        # 1. Train the Strategy (Calculate Slope/Offset/Etc)
        self.strategy.fit(stats_df, standards)

        results = []

        # 2. Iterate Samples
        for identifier, row in stats_df.iterrows():
            raw_val = row["mean"]
            raw_sem = row["sem"]
            if pd.isna(raw_sem):
                raw_sem = 0.0

            # 3. Generic Kragten Propagation
            corr, unc = self._generic_kragten(raw_val, raw_sem)

            # 4. Save
            results.append(
                CalculationResult(
                    identifier=str(identifier),
                    raw_mean=raw_val,
                    corrected_delta=corr,
                    combined_uncertainty=unc,
                    calibrated_with="/".join([s.name for s in standards]),
                )
            )

        return results

    def _generic_kragten(self, val, unc):
        """
        This works for ANY strategy (1-point, 2-point, Multi-point).
        It asks the strategy for parameters, then perturbs them blindly.
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
