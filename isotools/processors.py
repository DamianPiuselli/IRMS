"""
Data ingestion and preprocessing module.
Handles loading, renaming, and filtering of raw IRMS data.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
import pandas as pd


class IsotopeProcessor(ABC):
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
        self.exclude_rows = exclude_rows if exclude_rows else []

    @property
    @abstractmethod
    def target_column(self) -> str:
        """Name of the primary isotope column (e.g. 'd15n')."""

    @property
    @abstractmethod
    def isotope_mapping(self) -> Dict[str, str]:
        """Isotope-specific column mapping."""

    @property
    def column_mapping(self) -> Dict[str, str]:
        mapping = self.DEFAULT_MAPPING.copy()
        mapping.update(self.isotope_mapping)
        return mapping

    @abstractmethod
    def _filter_peaks(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def load_data(self, filepath: str, sheet_name: int | str = 0) -> pd.DataFrame:
        """
        Loads and standardizes raw data. Returns a CLEAN, RAW DataFrame.
        No aggregation is performed here.
        """
        df = pd.read_excel(filepath, sheet_name=sheet_name)

        # Standardize headers
        df.columns = df.columns.str.replace(r"\s+", " ", regex=True).str.strip()
        df = df.rename(columns=self.column_mapping)

        # Cleanup strings
        if "sample_name" in df.columns:
            df["sample_name"] = df["sample_name"].astype(str).str.strip()

        # Row Exclusion
        if self.exclude_rows and "row" in df.columns:
            df = df[~df["row"].isin(self.exclude_rows)]

        return self._filter_peaks(df)


class NitrogenProcessor(IsotopeProcessor):
    target_column = "d15n"

    @property
    def isotope_mapping(self) -> Dict[str, str]:
        return {
            "d 15N/14N": "d15n",
            "R 15N/14N": "r15n",
            "Ampl 28": "amp_28",
            "Ampl 29": "amp_29",
            "Area 28": "area_28",
            "Area 29": "area_29",
        }

    def _filter_peaks(self, df: pd.DataFrame) -> pd.DataFrame:
        # Default N2 processing often targets Peak 2 (Sample Gas)
        if "peak_nr" in df.columns:
            return df[df["peak_nr"] == 2].copy()
        return df
