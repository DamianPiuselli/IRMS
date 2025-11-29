from typing import List, Optional
import pandas as pd
from isotools.config import SystemConfig


class IsodatReader:
    """
    Handles reading and initial cleaning of Isodat Excel files.
    """

    def __init__(self, config: SystemConfig):
        self.config = config

    def read(
        self,
        filepath: str,
        sheet_name: int | str = 0,
        exclude_rows: Optional[List[int]] = None,
    ) -> pd.DataFrame:
        """
        Reads the file, renames columns, and filters rows based on config and user exclusions.
        """
        # 1. Load Data
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
        except Exception as e:
            raise IOError(f"Failed to read file {filepath}: {e}")

        # 2. Clean Headers (Remove double spaces, strip whitespace)
        # Isodat often outputs "Ampl  28" with two spaces.
        df.columns = df.columns.str.replace(r"\s+", " ", regex=True).str.strip()

        # 3. Rename Columns using Config
        df = df.rename(columns=self.config.column_mapping)

        # 4. Standardize Sample Names (String cleanup)
        if "sample_name" in df.columns:
            df["sample_name"] = df["sample_name"].astype(str).str.strip()

        # 5. Apply System Filtering (e.g. Keep only Peak 2 for N2)
        df = self.config.filter_func(df)

        # 6. Apply User Exclusions (Manual Row IDs)
        # Assumes 'row' column exists from Isodat mapping
        if exclude_rows and "row" in df.columns:
            df = df[~df["row"].isin(exclude_rows)]

        return df
