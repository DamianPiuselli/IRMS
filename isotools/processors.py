from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd


class IsotopeProcessor(ABC):
    """
    Abstract Base Class that defines the workflow for ANY isotope analysis.
    It orchestrates: Loading -> Filtering -> Aggregating.
    """

    def __init__(self, exclude_rows: Optional[List[int]] = None):
        """
        Args:
            exclude_rows: Optional list of Isodat 'Row' numbers to drop
                          (e.g., due to injector failure).
        """
        self.exclude_rows = exclude_rows if exclude_rows else []

    @property
    @abstractmethod
    def target_column(self) -> str:
        """The specific column name for the delta value (e.g. 'd 15N/14N')."""
        pass

    @abstractmethod
    def _filter_peaks(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Internal logic to select the correct peak (e.g. Peak 3 vs Peak 1).
        Must be implemented by concrete classes.
        """
        pass

    def load_data(
        self, filepath: str, sheet_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Orchestrates the loading process:
        1. Reads the raw Excel file (scanning for headers).
        2. Applies the 'exclude_rows' blacklist.
        3. Applies isotope-specific peak filtering.

        Returns:
            A clean DataFrame containing all raw replicates.
        """
        # 1. Use the dumb parser to get the file content
        df = pd.read_excel(filepath, sheet_name=sheet_name)

        # 2. Apply General Row Exclusion (Injector failures, etc.)
        if self.exclude_rows and "Row" in df.columns:
            # We invert the boolean mask (~) to KEEP rows NOT in the exclude list
            df = df[~df["Row"].isin(self.exclude_rows)]

        # 3. Apply Isotope Specific Logic (Peak selection)
        clean_df = self._filter_peaks(df)

        return clean_df

    def aggregate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Collapses replicates into Mean and Standard Error (SEM).
        Handles n=1 edge cases by setting SEM to 0.0.
        """
        # We group by the standard Isodat Identifier
        stats = df.groupby("Identifier 1")[self.target_column].agg(
            ["mean", "sem", "count"]
        )

        # Safety Fix: n=1 results in NaN for sem. We fill with 0.
        stats["sem"] = stats["sem"].fillna(0.0)

        return stats

    def process_file(
        self, filepath: str, sheet_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        High-level convenience method.
        Goes straight from Excel File -> Aggregated Stats.
        """
        raw_df = self.load_data(filepath, sheet_name=sheet_name)
        return self.aggregate(raw_df)


# --- CONCRETE IMPLEMENTATIONS ---


class NitrogenProcessor(IsotopeProcessor):
    """Processor for N2 analysis (d15N)."""

    target_column = "d 15N/14N"

    def _filter_peaks(self, df: pd.DataFrame) -> pd.DataFrame:
        # Nitrogen usually runs with Reference Gas on Peak 4
        # and Sample Gas on Peak 3. We want Peak 3.
        return df[df["Peak Nr"] == 2].copy()


# TODO: Implement SulfurProcessor, CarbonProcessor, etc. as needed.
# class SulfurProcessor(IsotopeProcessor):
#     """Processor for SO2 analysis (d34S)."""

#     target_column = 'd 34S/32S'

#     def _filter_peaks(self, df: pd.DataFrame) -> pd.DataFrame:
#         # Example logic: For SO2, maybe Peak 1 is the sample
#         # (This depends on your specific method/config)
#         return df[df['Peak Nr'] == 1].copy()

# class CarbonProcessor(IsotopeProcessor):
#     """Processor for CO2 analysis (d13C)."""

#     target_column = 'd 13C/12C'

#     def _filter_peaks(self, df: pd.DataFrame) -> pd.DataFrame:
#         # CO2 logic usually matches N2 (Peak 3), but sometimes varies.
#         return df[df['Peak Nr'] == 3].copy()
