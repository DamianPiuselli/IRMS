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
    # CRITICAL FIX: The DataFrame MUST contain the Standard's raw data
    # so the strategy can 'fit' it (calculate the offset).
    data = {
        "mean": [10.0, 10.0],  # 10.0 for STD_1 (Raw), 10.0 for Sample (Raw)
        "sem": [0.0, 0.0],  # 0 uncertainty for both
    }
    # Index must match the standard's name ("STD_1")
    df = pd.DataFrame(data, index=["STD_1", "Sample_X"])

    # 3. Run Calibration
    strategy = SinglePointStrategy()
    calib = Calibrator(strategy)

    # This will now find "STD_1" in df to calculate the offset (10 - 10 = 0)
    results = calib.calibrate(df, [std])

    # Find the result for the sample
    sample_res = next(r for r in results if r.identifier == "Sample_X")

    assert sample_res.combined_uncertainty == pytest.approx(0.0)


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
    results = calib.calibrate(df, [std])

    sample_res = next(r for r in results if r.identifier == "Sample_X")

    # Expected: sqrt(3^2 + 4^2) = 5.0
    assert sample_res.combined_uncertainty == pytest.approx(5.0, abs=1e-5)
