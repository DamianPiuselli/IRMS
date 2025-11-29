# isotools/models.py
from dataclasses import dataclass, field
from typing import List, Set


@dataclass
class ReferenceMaterial:
    """
    Immutable definition of a Reference Material.
    Includes true values and valid aliases for matching against raw data.
    """

    name: str
    d_true: float  # Certified Delta Value
    u_true: float  # Certified Uncertainty (1 sigma)
    aliases: List[str] = field(default_factory=list)

    # Internal cache for fast lookups
    _lookup_set: Set[str] = field(init=False, repr=False)

    def __post_init__(self):
        if self.u_true < 0:
            raise ValueError(f"Uncertainty for {self.name} cannot be negative.")

        # Normalize aliases to lowercase for case-insensitive matching
        self._lookup_set = {self.name.lower()} | {a.lower() for a in self.aliases}

    def matches(self, sample_name: str) -> bool:
        """
        Returns True if the provided sample_name matches this standard
        or any of its aliases.
        """
        if not isinstance(sample_name, str):
            return False
        return sample_name.strip().lower() in self._lookup_set

    def __repr__(self) -> str:
        return f"<RefMat {self.name}: {self.d_true} ± {self.u_true}>"
