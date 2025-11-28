"""
Reporting and Aggregation module.
Handles the transition from Raw/Calibrated data to Summary Statistics.
"""

import pandas as pd


def aggregate_samples(df: pd.DataFrame, group_col: str = "sample_name") -> pd.DataFrame:
    """
    Generic aggregator for IRMS data.
    Calculates Mean, SEM, and Count for all numeric columns.
    """
    # Select numeric columns only
    numeric_cols = df.select_dtypes(include="number").columns

    # Define aggregation dictionary
    aggs = {col: ["mean", "sem", "count"] for col in numeric_cols}

    # Perform grouping
    stats = df.groupby(group_col).agg(aggs)

    # Flatten MultiIndex (e.g. 'd15n_mean')
    stats.columns = ["_".join(col).strip() for col in stats.columns.values]

    # Fill NaN SEMs (for n=1 samples)
    sem_cols = [c for c in stats.columns if "sem" in c]
    stats[sem_cols] = stats[sem_cols].fillna(0.0)

    return stats


class Reporter:
    """
    Helper to format technical summary tables into client-ready reports.
    """

    def __init__(self, decimals: int = 2):
        self.decimals = decimals

    def create_report(
        self, summary_df: pd.DataFrame, target_col: str = "d15n"
    ) -> pd.DataFrame:
        """
        Creates a polished report from an aggregated dataframe.
        Strictly reports 'combined_uncertainty' if available.
        Does NOT fallback to standard error (SEM).
        """
        df = summary_df.copy()

        # Define Mapping: {Internal Column Name: Final Report Header}
        col_map = {}

        # 1. Primary Isotopic Value
        if "corrected_delta_mean" in df.columns:
            # Calibrated Data
            col_map["corrected_delta_mean"] = f"Delta {target_col.upper()} (Air)"

            # 2. Uncertainty Logic
            # ONLY report rigorous uncertainty. No fallbacks to precision (SEM).
            if "combined_uncertainty" in df.columns:
                col_map["combined_uncertainty"] = "Uncertainty (1s)"

        else:
            # Uncalibrated / Raw Data
            col_map[f"{target_col}_mean"] = f"Delta {target_col.upper()} (Raw)"
            # No uncertainty reported for raw data (as it is purely precision)

        # 3. Sample Count (N)
        # We can take count from any column, usually the target
        count_col = f"{target_col}_count"
        if count_col in df.columns:
            col_map[count_col] = "N"

        # Filter: Only grab columns that actually exist
        # Using direct iteration over col_map for Pythonic style
        available_cols = [c for c in col_map if c in df.columns]

        # Create final dataframe
        report = df[available_cols].rename(columns=col_map)

        return report.round(self.decimals)
