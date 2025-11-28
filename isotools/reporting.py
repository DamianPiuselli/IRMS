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
        Prioritizes 'corrected_delta' if available, falls back to 'target_col'.
        """
        df = summary_df.copy()

        # Mapping logic
        col_map = {}

        # Primary Value
        if "corrected_delta_mean" in df.columns:
            col_map["corrected_delta_mean"] = f"Delta {target_col} (Air)"
            col_map["corrected_delta_sem"] = "Error (1s)"
        else:
            col_map[f"{target_col}_mean"] = f"Delta {target_col} (Raw)"
            col_map[f"{target_col}_sem"] = "Error (1s)"

        # Count
        # We can take count from any column, usually the target
        count_col = f"{target_col}_count"
        if count_col in df.columns:
            col_map[count_col] = "N"

        # Filter and Rename
        available_cols = [c for c in col_map if c in df.columns]
        report = df[available_cols].rename(columns=col_map)

        return report.round(self.decimals)
