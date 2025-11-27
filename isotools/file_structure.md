isotools/
├── __init__.py
├── schemas.py          # Definitions (Dataclasses) for Standards/Results
├── processors.py       # The specific logic for N2, SO2, H2 (The Strategy Pattern)
├── calibration.py      # The shared math (FIRMS, Kragten)
├── standards_db.py      # database of standards and known substances
├── strategies.py        # Strategy design pattern implementations for calibration
└── visualization.py    # Plotting tools