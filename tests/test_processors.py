import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from isotools.processors import NitrogenProcessor


@pytest.fixture
def mock_read_excel():
    """Patches pandas read_excel to return a test dataframe."""
    with patch("pandas.read_excel") as mock:
        yield mock


def test_load_data_renaming(mock_read_excel):
    """Test that load_data correctly renames Isodat columns."""
    # Setup raw data mimicking Isodat format
    raw_data = {
        "Identifier 1": ["Sample A", "Sample A"],
        "Peak Nr": [2, 3],
        "d 15N/14N": [5.5, 6.0],
        "Ampl  28": [1000, 1000],  # Note the double space
        "Row": [1, 1],
    }
    mock_read_excel.return_value = pd.DataFrame(raw_data)

    proc = NitrogenProcessor()

    # Run load_data (filepath is dummy since we mock read_excel)
    df = proc.load_data("dummy.xls")

    # Assertions
    assert "d15n" in df.columns, "Column renaming failed"
    assert "amp_28" in df.columns, "Whitespace normalization failed"
    assert "sample_name" in df.columns


def test_peak_filtering_default(mock_read_excel):
    """Test that NitrogenProcessor filters for Peak 2 by default."""
    raw_data = {
        "Identifier 1": ["S1", "S1"],
        "Peak Nr": [1, 2],  # Peak 1 (Ref), Peak 2 (Sample)
        "d 15N/14N": [0.0, 10.0],
        "Row": [1, 1],
    }
    mock_read_excel.return_value = pd.DataFrame(raw_data)

    proc = NitrogenProcessor()  # No args, defaults to peak 2 logic
    df = proc.load_data("dummy.xls")

    assert len(df) == 1
    assert df.iloc[0]["peak_nr"] == 2
    assert df.iloc[0]["d15n"] == 10.0


def test_exclude_rows(mock_read_excel):
    """Test that specific rows can be excluded."""
    raw_data = {
        "Identifier 1": ["S1", "S2"],
        "Peak Nr": [2, 2],
        "d 15N/14N": [10.0, 12.0],
        "Row": [1, 2],  # We want to exclude row 2
    }
    mock_read_excel.return_value = pd.DataFrame(raw_data)

    proc = NitrogenProcessor(exclude_rows=[2])
    df = proc.load_data("dummy.xls")

    assert len(df) == 1
    assert df.iloc[0]["row"] == 1
