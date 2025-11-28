# isotools/visualization.py
import matplotlib.pyplot as plt
import seaborn as sns
from .processors import IsotopeProcessor  # For type hinting


def plot_diagnostics(raw_df, results, standards, processor: IsotopeProcessor):
    """
    Creates a diagnostic panel that adapts to the specific isotope system.

    Args:
        raw_df: DataFrame with standardized columns.
        results: List of CalculationResult objects.
        standards: List of ReferenceMaterial objects.
        processor: The processor instance used (provides column names).
    """
    # 1. Dynamically get the column names
    delta_col = processor.target_column  # e.g., "d15n" or "d13c"
    amp_col = processor.amplitude_column  # e.g., "amp_28" or "amp_44"

    # Generate label strings for the plot axes
    delta_label = rf"Raw $\delta${delta_col[1:].upper()}"  # d15n -> Raw d15N

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # --- PLOT 1: SOURCE LINEARITY ---

    # Calculate Deviation using dynamic column name
    # (Deviation = Raw Delta - Mean of that Sample)
    sample_means = raw_df.groupby("sample_name")[delta_col].transform("mean")

    raw_df = raw_df.copy()
    raw_df["centered_delta"] = raw_df[delta_col] - sample_means

    # Plot using dynamic columns
    sns.scatterplot(
        data=raw_df,
        x=amp_col,  # Dynamic X-Axis
        y="centered_delta",
        hue="sample_name",
        alpha=0.6,
        ax=ax1,
        legend=False,
    )

    sns.regplot(
        data=raw_df,
        x=amp_col,  # Dynamic X-Axis
        y="centered_delta",
        scatter=False,
        ax=ax1,
        color="red",
    )

    ax1.set_title(f"Source Linearity Check\n({amp_col} vs {delta_col})")
    ax1.set_xlabel("Signal Amplitude (mV)")
    ax1.set_ylabel("Deviation from Sample Mean (‰)")

    # --- PLOT 2: CALIBRATION ACCURACY ---

    std_names = [s.name for s in standards]
    std_results = [r for r in results if r.identifier in std_names]

    if not std_results:
        ax2.text(0.5, 0.5, "No Standards Found", ha="center")
    else:
        y_residuals = []
        x_predicted = []

        for res in std_results:
            std_ref = next((s for s in standards if s.name == res.identifier), None)
            if std_ref:
                resid = res.corrected_delta - std_ref.true_delta
                y_residuals.append(resid)
                x_predicted.append(res.corrected_delta)

        ax2.scatter(x_predicted, y_residuals, color="blue", s=100, edgecolor="k")
        ax2.axhline(0, color="black", linestyle="--")
        ax2.set_title("Calibration Accuracy (Residuals)")
        ax2.set_xlabel(f"Corrected {delta_label} (‰)")

    plt.tight_layout()
    return fig
