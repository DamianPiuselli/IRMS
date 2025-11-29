[![Pylint](https://github.com/DamianPiuselli/IRMS/actions/workflows/pylint.yml/badge.svg)](https://github.com/DamianPiuselli/IRMS/actions/workflows/pylint.yml)

# isotools

**isotools** is a Python library designed for the automated processing, normalization, and uncertainty propagation of Stable Isotope Ratio Mass Spectrometry (IRMS) data.

It moves away from procedural scripts to a **Batch-Centric** workflow, where data, configuration, and calibration logic are encapsulated in a single, robust object.

## Key Features

* **Batch-Centric Workflow:** Manage an entire analytical run as a single object (`Batch`) that handles data state from raw import to final reporting.
* **Rigorous Uncertainty:** Implements **Kragten numerical differentiation** to propagate uncertainty from standards to samples, combining both systematic calibration error and random measurement noise.
* **Flexible Standards:** Built-in database of Reference Materials (USGS32, USGS34, etc.) with support for **aliasing** (e.g., automatically recognizes "USGS-32", "st_usgs32").
* **Configurable Systems:** Easily extensible to different gas systems ($N_2$, $CO_2$, $SO_2$) via `SystemConfig` objects.
* **Modular Strategies:** Switch calibration math (e.g., 2-Point Linear, Single-Point Offset) without rewriting your workflow.

## Installation

This package is designed to be installed in editable mode for local development.

## Quick Start

see `workflow.ipynb` for a basic usage example.

```python
import isotools
from isotools import Batch, Nitrogen, TwoPointLinear
from isotools.standards import USGS32, USGS34, USGS35

# 1. Initialize the Batch
# Reads the Isodat file and applies N2-specific cleaning rules (Peak 2 only, column renaming)
run = Batch("DATA/nitrate_2025.xls", config=Nitrogen)

# 2. Inspect Data (Optional)
# Check what samples were found to decide on exclusions
print(run.data_view)

# 3. Clean Data
# Exclude bad injections by Row ID (e.g., Row 26 had a pressure drop)
run.exclude_rows([26])

# 4. Configure Standards
# Set Anchors: Used to build the calibration curve
run.set_anchors(["USGS32", "USGS34"]) 

# Set Controls: Used for QC (Trueness check), not fitting
run.set_controls(["USGS35"])

# 5. Process
# Aggregates replicates, fits the curve, and propagates uncertainty
run.process(strategy=TwoPointLinear())

# 6. Get Results
print(run.report)  # Final table with corrected values and combined uncertainty
print(run.qaqc)    # Trueness report for Control standards
```

```bash
cd /path/to/isotools_folder
pip install -e .