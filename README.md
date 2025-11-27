# isotools

**isotools** is a Python library designed for the automated processing, aggregation, and normalization of Stable Isotope Ratio Mass Spectrometry (IRMS) data. 

It handles raw Isodat exports, manages isotope-specific logic (e.g., N2 vs. SO2), and performs rigorous uncertainty propagation using the Kragten method.

## Key Features

* **Smart Ingestion:** Automatically detects headers and filters Isodat `.xlsx` exports.
* **Processor Pattern:** Encapsulates logic for specific isotopes (e.g., peak selection for $\delta^{15}N$ vs $\delta^{34}S$).
* **Flexible Calibration:** Supports modular strategies (Single-Point, Two-Point Linear, etc.).
* **Uncertainty Propagation:** Implements the Kragten numerical differentiation method to calculate combined standard uncertainty ($u_c$) for every sample.
* **Standardized Database:** Built-in definitions for common reference materials (USGS32, USGS34, etc.).

## Installation

This package is designed to be installed in editable mode for local development.

```bash
cd /path/to/isotools_folder
pip install -e .