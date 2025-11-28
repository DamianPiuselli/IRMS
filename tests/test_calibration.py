import pandas as pd
import pytest
from isotools.calibration import Calibrator
from isotools.strategies import SinglePointStrategy, TwoPointStrategy
from isotools.schemas import ReferenceMaterial


def test_single_point_offset_calibration():
    """
    Test that SinglePointStrategy correctly applies a constant offset
    to all raw data points.
    """
    # 1. Setup Standards
    # True value = 10.0. Raw measures = 8.0. Offset should be +2.0.
    std = ReferenceMaterial(name="STD_1", true_delta=10.0, uncertainty_1s=0.0)

    # 2. Setup Raw DataFrame
    # Two samples: The standard itself, and a sample to correct
    data = {
        "sample_name": ["STD_1", "STD_1", "Sample_X", "Sample_X"],
        "d15n": [8.0, 8.0, 15.0, 20.0],
        # Add amplitude just to have a complete-looking frame
        "amp_28": [100, 100, 100, 100],
    }
    raw_df = pd.DataFrame(data)

    # 3. Run Calibration
    strategy = SinglePointStrategy()
    calib = Calibrator(strategy)

    # Calibrate (this calculates offset from STD_1 rows)
    result_df = calib.calibrate(raw_df, standards=[std], target_col="d15n")

    # 4. Assertions
    # Check that the corrected_delta column exists
    assert "corrected_delta" in result_df.columns

    # Verify Standard is corrected to its True Value (8 + 2 = 10)
    std_results = result_df[result_df["sample_name"] == "STD_1"]["corrected_delta"]
    assert all(val == pytest.approx(10.0) for val in std_results)

    # Verify Sample is corrected by the same offset (15 + 2 = 17, 20 + 2 = 22)
    sample_results = result_df[result_df["sample_name"] == "Sample_X"][
        "corrected_delta"
    ].values
    assert sample_results[0] == pytest.approx(17.0)
    assert sample_results[1] == pytest.approx(22.0)


def test_two_point_linear_calibration():
    """
    Test 2-point calibration (slope and intercept).
    """
    # 1. Setup Standards
    # Std A: Raw=10, True=20 (Point 1)
    # Std B: Raw=30, True=60 (Point 2)
    # Slope = (60-20)/(30-10) = 40/20 = 2.0
    # Intercept = 20 - (2*10) = 0.0
    # Equation: y = 2x
    std_a = ReferenceMaterial(name="STD_A", true_delta=20.0, uncertainty_1s=0.0)
    std_b = ReferenceMaterial(name="STD_B", true_delta=60.0, uncertainty_1s=0.0)

    # 2. Setup Raw DataFrame
    data = {"sample_name": ["STD_A", "STD_B", "Unknown"], "d15n": [10.0, 30.0, 5.0]}
    raw_df = pd.DataFrame(data)

    # 3. Run Calibration
    calib = Calibrator(TwoPointStrategy())
    result_df = calib.calibrate(raw_df, standards=[std_a, std_b], target_col="d15n")

    # 4. Assertions
    # Unknown: 5.0 * 2 = 10.0
    unknown_val = result_df[result_df["sample_name"] == "Unknown"][
        "corrected_delta"
    ].iloc[0]
    assert unknown_val == pytest.approx(10.0)
