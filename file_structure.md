isotools/
├── __init__.py
├── schemas.py          # Definitions (Dataclasses) for Standards/Results
├── processors.py       # The specific logic for N2, SO2, H2 
├── calibration.py      # The shared math of calibration and uncertainty propagation
├── standards.py      # database of standards and known substances
├── strategies.py        # Strategy design pattern implementations for calibration types
└── visualization.py    # Plotting tools