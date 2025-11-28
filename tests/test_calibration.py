import pandas as pd
import pytest
from isotools.calibration import Calibrator
from isotools.strategies import SinglePointStrategy
from isotools.schemas import ReferenceMaterial


def test_kragten_zero_uncertainty():
    """
    If inputs have 0 uncertainty, output uncertainty must be 0.
    """
    # 1. Setup Standards
    # We define a standard with 0 uncertainty
    std = ReferenceMaterial("STD_1", 10.0, 0.0)

    # 2. Setup Dataframe
    # We assume 'sample_name' is the index, or you set it as index before calibration
    data = {
        "mean": [10.0, 10.0],  # 10.0 for STD_1 (Raw), 10.0 for Sample (Raw)
        "sem": [0.0, 0.0],  # 0 uncertainty for both
    }
    df = pd.DataFrame(data, index=["STD_1", "Sample_X"])

    # 3. Run Calibration
    strategy = SinglePointStrategy()
    calib = Calibrator(strategy)

    # The method now returns a DataFrame
    results_df = calib.calibrate(df, [std])

    # 4. Assertions using DataFrame indexing
    # We look up the row "Sample_X" and the column "combined_uncertainty"
    actual_uncertainty = results_df.loc["Sample_X", "combined_uncertainty"]

    assert actual_uncertainty == pytest.approx(0.0)


def test_kragten_simple_propagation():
    """
    For Single Point (Offset): u_c = sqrt(u_sample^2 + u_std^2)
    If u_sample=3 and u_std=4, u_c must be 5 (3-4-5 triangle).
    """
    # Standard has uncertainty of 4.0
    std = ReferenceMaterial("STD_1", 100.0, 4.0)

    # Sample has uncertainty of 3.0
    # Standard Raw = 100 (matches True 100, so Offset=0)
    # Standard Raw SEM = 0 (to isolate the effect of the certified uncertainty)
    data = {"mean": [100.0, 100.0], "sem": [0.0, 3.0]}
    df = pd.DataFrame(data, index=["STD_1", "Sample_X"])

    strategy = SinglePointStrategy()
    calib = Calibrator(strategy)

    # Returns DataFrame
    results_df = calib.calibrate(df, [std])

    # Access result for Sample_X
    actual_uncertainty = results_df.loc["Sample_X", "combined_uncertainty"]

    # Expected: sqrt(3^2 + 4^2) = 5.0
    assert actual_uncertainty == pytest.approx(5.0, abs=1e-5)
