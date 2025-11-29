isotools/
├── core.py             # The 'Batch' controller
├── config.py           # System configurations (Nitrogen, etc.)
├── models.py           # Data classes (ReferenceMaterial)
├── standards.py        # Database of known materials
├── strategies/         # Mathematical calibration logic
│   ├── abstract.py
│   └── normalization.py
└── utils/
    ├── readers.py      # Isodat file parsing
    └── kragten.py      # Uncertainty propagation math