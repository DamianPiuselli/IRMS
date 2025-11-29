from dataclasses import dataclass, field
from typing import Dict, Callable
import pandas as pd


@dataclass
class SystemConfig:
    """
    Configuration for a specific isotope system (e.g., N2, CO2).
    Defines how to interpret the raw Isodat file columns and rows.
    """

    name: str
    target_column: str
    column_mapping: Dict[str, str]
    # A function that takes the raw DF and returns the filtered DF (e.g. keeping specific peaks)
    filter_func: Callable[[pd.DataFrame], pd.DataFrame] = field(default=lambda df: df)


# --- Logic Helpers ---
def _filter_n2_peaks(df: pd.DataFrame) -> pd.DataFrame:
    """Standard N2 logic: Keep Peak 2 (Sample Gas)."""
    if "peak_nr" in df.columns:
        return df[df["peak_nr"] == 2].copy()
    return df


# --- Configurations ---

NITROGEN_MAPPING = {
    # Standard Isodat Columns
    "Row": "row",
    "Identifier 1": "sample_name",
    "Identifier 2": "sample_id_2",
    "Peak Nr": "peak_nr",
    "Amount": "amount",
    "Area All": "area_all",
    "Comment": "comment",
    # N2 Specifics
    "d 15N/14N": "d15n",
    "R 15N/14N": "r15n",
    "Ampl 28": "amp_28",
    "Ampl 29": "amp_29",
    "Area 28": "area_28",
    "Area 29": "area_29",
}

# The public object you will use in your scripts
Nitrogen = SystemConfig(
    name="Nitrogen (N2)",
    target_column="d15n",
    column_mapping=NITROGEN_MAPPING,
    filter_func=_filter_n2_peaks,
)
