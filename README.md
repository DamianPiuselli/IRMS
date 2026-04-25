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

Clone the repository and install the dependencies:

```bash
git clone https://github.com/DamianPiuselli/IRMS.git
cd IRMS
pip install -r requirements.txt
```

For development (testing and linting), install:
```bash
pip install -r requirements-dev.txt
```