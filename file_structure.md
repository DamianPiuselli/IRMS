/Users/damm/Projects/IRMS/
├── .github/            # GitHub Actions (CI/CD)
├── DATA/               # Example raw data files
├── isotools/           # Main package source
│   ├── core.py         # The 'Batch' controller
│   ├── config.py       # System configurations (Nitrogen, etc.)
│   ├── models.py       # Data classes (ReferenceMaterial)
│   ├── standards.py    # Database of known materials
│   ├── strategies/     # Mathematical calibration logic
│   │   ├── abstract.py
│   │   └── normalization.py
│   └── utils/
│       ├── readers.py  # Isodat file parsing
│       └── kragten.py  # Uncertainty propagation math
├── tests/              # Test suite
├── GEMINI.md           # LLM agent instructions and context
├── README.md           # Project overview and installation
├── requirements.txt    # Core dependencies
├── requirements-dev.txt # Development dependencies
├── .pylintrc           # Linting configuration
└── workflow.ipynb      # Usage example notebook
