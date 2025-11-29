# isotools/standards.py
from .models import ReferenceMaterial

# --- Nitrogen Standards ---
USGS32 = ReferenceMaterial(
    name="USGS32",
    d_true=180.0,
    u_true=1.0,
    aliases=[
        "USGS-32",
        "KN032",
    ],
)

USGS34 = ReferenceMaterial(
    name="USGS34", d_true=-1.8, u_true=0.2, aliases=["USGS-34", "KN034"]
)

USGS35 = ReferenceMaterial(
    name="USGS35", d_true=2.7, u_true=0.2, aliases=["USGS-35", "KN035"]
)

# --- Registry & Lookup ---
# This list defines what the library "knows" by default.
DEFAULT_STANDARDS = [USGS32, USGS34, USGS35]


def get_standard(name: str, custom_standards: list = None) -> ReferenceMaterial:
    """
    Attempts to find a ReferenceMaterial object matching the given name.
    Checks custom_standards first (if provided), then defaults.
    Returns None if no match found.
    """
    registry = (custom_standards or []) + DEFAULT_STANDARDS

    for std in registry:
        if std.matches(name):
            return std
    return None
