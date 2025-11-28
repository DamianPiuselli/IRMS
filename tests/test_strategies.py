import pandas as pd
import pytest
from isotools.strategies import TwoPointStrategy
from isotools.schemas import ReferenceMaterial


def test_two_point_strategy_perfect_linearity():
    """
    If standards follow y = 2x + 1 exactly, the strategy must recover this.
    """
    # 1. Setup Standards: True = 2 * Raw + 1
    # Std A: Raw=10 -> True=21
    # Std B: Raw=20 -> True=41
    std_a = ReferenceMaterial(name="STD_A", true_delta=21.0, uncertainty_1s=0.0)
    std_b = ReferenceMaterial(name="STD_B", true_delta=41.0, uncertainty_1s=0.0)

    # Create Stats DataFrame (Simulating what Processor.aggregate returns)
    stats_data = {"mean": [10.0, 20.0], "sem": [0.0, 0.0]}
    stats_df = pd.DataFrame(stats_data, index=["STD_A", "STD_B"])

    # 2. Fit
    strategy = TwoPointStrategy()
    strategy.fit(stats_df, [std_a, std_b])

    # 3. Predict Sample (Raw=50 -> Should be 2*50 + 1 = 101)
    result = strategy.predict(50.0)

    assert result == pytest.approx(101.0, abs=1e-9)
