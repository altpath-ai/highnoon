"""
HTC — Hedonic Teleology Classification

Purpose codes: what human end is being served, at what quality.
"""

from dataclasses import dataclass, field


QUALITY_MODIFIERS = [
    "scope",            # How much of the activity is addressed (partial → complete)
    "accuracy",         # How correct/reliable (approximate → precise)
    "personalization",  # How tailored to the individual (generic → bespoke)
    "fidelity",         # How close to the ideal outcome (degraded → perfect)
    "continuity",       # How consistently maintained (intermittent → continuous)
    "agency",           # How much user control preserved (prescribed → sovereign)
    "inclusivity",      # How many people can it serve (restricted → universal)
]


@dataclass
class HTC:
    """A Hedonic Teleology Classification — a purpose code."""
    domain_code: str
    activity: str = ""
    quality: dict = field(default_factory=dict)
    description: str = ""

    @property
    def code(self) -> str:
        if self.activity:
            return f"{self.domain_code}.{self.activity}"
        return self.domain_code

    def __str__(self) -> str:
        quals = ", ".join(f"{k}:{v}" for k, v in self.quality.items())
        qual_str = f" {{{quals}}}" if quals else ""
        return f"HTC {self.code}{qual_str}"
