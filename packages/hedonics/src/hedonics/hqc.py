"""
HQC — Hedonic Quality Cost
HQCM — Hedonic Quality Cost Modifier

Cost codes: what resources are consumed/freed, and how.
All costs are fungible — freed resources can be redeployed to any purpose.
"""

from dataclasses import dataclass, field


COST_CATEGORIES = {
    "T": "TIME",
    "F": "FINANCIAL",
    "A": "ATTENTION",
    "P": "PHYSICAL",
    "S": "SOCIAL",
    "E": "ENVIRONMENTAL",
    "R": "REGULATORY",
    "K": "KNOWLEDGE",
    "X": "STATUS",
}

COST_MODIFIERS = [
    "direction",        # Does software increase or decrease cost (increased ↔ decreased)
    "magnitude",        # By how much (marginal → eliminated)
    "visibility",       # Is the modification obvious (transparent → opaque)
    "distribution",     # Who experiences the cost change (user → third-party → society)
    "temporality",      # When does the modification take effect (immediate → deferred)
    "reversibility",    # Can the original cost structure return (reversible → permanent)
    "conditionality",   # Is the modification guaranteed (guaranteed → conditional)
]


@dataclass
class HQCM:
    """A Hedonic Quality Cost Modifier — how software changes a cost."""
    direction: str = ""         # increased | decreased
    magnitude: str = ""         # marginal | moderate | significant | eliminated
    visibility: str = ""        # transparent | opaque
    distribution: str = ""      # user | third-party | society
    temporality: str = ""       # immediate | ongoing | deferred
    reversibility: str = ""     # reversible | slow | permanent
    conditionality: str = ""    # guaranteed | conditional

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v}


@dataclass
class HQC:
    """A Hedonic Quality Cost — a cost classification with modifiers."""
    category: str           # T, F, A, P, S, E, R, K, X
    subcategory: str = ""   # e.g., T.1 (labor time), F.1 (direct expenditure)
    description: str = ""
    modifier: HQCM = field(default_factory=HQCM)

    @property
    def code(self) -> str:
        if self.subcategory:
            return f"{self.category}.{self.subcategory}"
        return self.category

    @property
    def category_name(self) -> str:
        return COST_CATEGORIES.get(self.category, "UNKNOWN")

    def __str__(self) -> str:
        mods = self.modifier.to_dict()
        mod_str = f" {mods}" if mods else ""
        return f"HQC {self.code} ({self.category_name}){mod_str}"
