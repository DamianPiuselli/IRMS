import pandas as pd
import pytest
from isotools.processors import NitrogenProcessor


def test_schema_validation_failure():
    """Should raise ValueError if 'Identifier 1' is missing."""
    # Bad Data: Missing 'Identifier 1' (which maps to 'sample_name')
    bad_df = pd.DataFrame({"Row": [1], "Peak Nr": [2], "d 15N/14N": [5.0]})

    proc = NitrogenProcessor()

    # CRITICAL FIX: Do not call load_data("dummy").
    # Instead, pass the dataframe directly to the internal validation methods.
    # We expect a ValueError because the required 'sample_name' column will be missing.
    with pytest.raises(ValueError, match="missing required columns"):
        # pylint: disable=protected-access
        std_df = proc._standardize_schema(bad_df)
        proc._validate_schema(std_df)


def test_peak_filtering():
    """Should only keep the target peak."""
    # Setup: 3 rows, representing one acquisition cycle
    df = pd.DataFrame(
        {
            "Identifier 1": ["S1", "S1", "S1"],
            "Peak Nr": [1, 2, 3],  # Peaks 1, 2, 3
            "d 15N/14N": [0.0, 10.0, 0.0],
            "Row": [1, 1, 1],
            "Amount": [1, 1, 1],
            "Area 28": [100, 100, 100],  # Added to satisfy new Nitrogen mapping
            "Area 29": [1, 1, 1],
            "Ampl 28": [500, 500, 500],
            "Ampl 29": [5, 5, 5],
        }
    )

    # Initialize processor looking for Peak 2
    proc = NitrogenProcessor(target_peak=2)

    # pylint: disable=protected-access
    # Run the pipeline steps manually on the DataFrame
    df_std = proc._standardize_schema(df)
    df_filtered = proc._filter_peaks(df_std)

    # Assertions
    assert len(df_filtered) == 1
    assert df_filtered.iloc[0]["peak_nr"] == 2
    assert df_filtered.iloc[0]["d15n"] == 10.0
