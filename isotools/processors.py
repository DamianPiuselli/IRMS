"""
Data ingestion and preprocessing module.

This module defines the `IsotopeProcessor` abstract base class and concrete implementations
(e.g., `NitrogenProcessor`). It handles the critical "ETL" (Extract, Transform, Load) steps:
1. Loading raw Excel files from Isodat.
2. Standardizing column names (renaming to snake_case).
3. Validating that essential columns exist.
4. Filtering rows (e.g., specific peaks, excluding bad injections).
5. Aggregating replicates into mean and standard error.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
import pandas as pd


class IsotopeProcessor(ABC):
    """
    Abstract Base Class that orchestrates the data processing workflow.

    Subclasses must define:
    1. `target_column`: The final column name for the delta value (after renaming).
    2. `isotope_mapping`: A dictionary mapping raw headers to standardized names
       specific to that isotope.
    3. `_filter_peaks`: Logic to select the correct peak rows.
    """

    # --- STANDARD COLUMNS (Shared across all IRMS methods) ---
    # These map the raw Isodat headers to clean internal names.
    # Subclasses should NOT redefine these unless they need to override them.
    DEFAULT_MAPPING = {
        "Row": "row",
        "Identifier 1": "sample_name",
        "Identifier 2": "sample_id_2",
        "Peak Nr": "peak_nr",
        "Amount": "amount",
        "Area All": "area_all",
        "Comment": "comment",
    }

    def __init__(self, exclude_rows: Optional[List[int]] = None):
        """
        Args:
            exclude_rows: Optional list of 'Row' numbers (integers) to drop
                          before processing (e.g., due to autosampler errors).
        """
        self.exclude_rows = exclude_rows if exclude_rows else []

    @property
    @abstractmethod
    def target_column(self) -> str:
        """
        The name of the column containing the primary isotopic value
        (e.g., 'd15n' or 'd13c') *AFTER* renaming has occurred.
        """

    @property
    @abstractmethod
    def isotope_mapping(self) -> Dict[str, str]:
        """
        Returns a dictionary of column mappings specific to this isotope system.
        Example: {'d 15N/14N': 'd15n', 'Ampl 28': 'amp_28'}

        This will be merged with DEFAULT_MAPPING.
        """

    @property
    def column_mapping(self) -> Dict[str, str]:
        """
        Combines the default mapping with the subclass-specific mapping.
        """
        mapping = self.DEFAULT_MAPPING.copy()
        mapping.update(self.isotope_mapping)
        return mapping

    @property
    def required_columns(self) -> List[str]:
        """
        List of columns that MUST be present in the dataframe after renaming.
        Used for validation.
        """
        return ["sample_name", "peak_nr", "row", self.target_column]

    @abstractmethod
    def _filter_peaks(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Implementation-specific logic to select the correct rows.
        Usually involves filtering by 'peak_nr'.
        """

    def _standardize_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies column renaming and basic type cleanup.
        """
        # 1. NEW: Normalize whitespace in headers (collapse multi-spaces to single)
        # This turns "Ampl  28" into "Ampl 28" automatically
        df.columns = df.columns.str.replace(r"\s+", " ", regex=True).str.strip()

        # 2. Rename columns based on the full mapping (which uses single spaces)
        df = df.rename(columns=self.column_mapping)

        # 3. String cleanup
        if "sample_name" in df.columns:
            df["sample_name"] = df["sample_name"].astype(str).str.strip()

        return df

    def _validate_schema(self, df: pd.DataFrame):
        """
        Ensures the dataframe has the minimum necessary structure to proceed.
        Raises ValueError if critical columns are missing.
        """
        missing = [col for col in self.required_columns if col not in df.columns]

        if missing:
            # We raise an error to fail fast rather than letting pandas
            # throw a confusing KeyError later during aggregation.
            raise ValueError(
                f"Input file is missing required columns: {missing}.\n"
                f"Did the Isodat export format change?\n"
                f"Columns found: {list(df.columns)}"
            )

    def load_data(
        self, filepath: str, sheet_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        The main ingestion pipeline.

        Steps:
        1. Read Excel file.
        2. Rename columns (Standardize).
        3. Validate schema.
        4. Exclude specific rows (Blacklist).
        5. Filter for relevant peaks.
        """
        # 1. Read Raw
        df = pd.read_excel(filepath, sheet_name=sheet_name)

        # 2. Standardize Names
        df = self._standardize_schema(df)

        # 3. Validate
        self._validate_schema(df)

        # 4. Exclude Rows (using standardized 'row' column)
        if self.exclude_rows and "row" in df.columns:
            df = df[~df["row"].isin(self.exclude_rows)]

        # 5. Filter Peaks
        clean_df = self._filter_peaks(df)

        return clean_df

    def aggregate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Groups replicates by 'sample_name' and calculates Mean and Standard Error (SEM).

        Returns:
            DataFrame indexed by 'sample_name' with columns [mean, sem, count].
        """
        stats = df.groupby("sample_name")[self.target_column].agg(
            ["mean", "sem", "count"]
        )

        # Handle n=1 cases where sem is NaN (replace with 0.0)
        stats["sem"] = stats["sem"].fillna(0.0)

        return stats

    def process_file(
        self, filepath: str, sheet_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Convenience wrapper to go from File -> Aggregated Stats in one call.
        """
        raw_df = self.load_data(filepath, sheet_name=sheet_name)
        return self.aggregate(raw_df)


# --- CONCRETE IMPLEMENTATIONS ---


class NitrogenProcessor(IsotopeProcessor):
    """
    Processor for N2 analysis (d15N).

    Standardizes N2-specific columns and filters for the sample gas peak.
    """

    # The internal standardized name we want to use for analysis
    target_column = "d15n"

    def __init__(self, exclude_rows: Optional[List[int]] = None, target_peak: int = 2):
        """
        Args:
            exclude_rows: List of row numbers to drop.
            target_peak: The Peak Nr of the sample gas (default=2).
        """
        super().__init__(exclude_rows)
        self.target_peak = target_peak

    @property
    def isotope_mapping(self) -> Dict[str, str]:
        """
        Maps Isodat's N2 specific headers to our internal snake_case names.
        """
        return {
            "d 15N/14N": "d15n",
            "R 15N/14N": "r15n",
            "Ampl 28": "amp_28",
            "Ampl 29": "amp_29",
            "Area 28": "area_28",
            "Area 29": "area_29",
        }

    def _filter_peaks(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filters the dataframe to keep only the configured sample peak.
        """
        # Note: We use "peak_nr" because columns have already been renamed by this point.
        return df[df["peak_nr"] == self.target_peak].copy()
