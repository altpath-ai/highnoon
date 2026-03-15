"""
HQC — Hedonic Quality Cost
HQCM — Hedonic Quality Cost Modifier

Cost codes: what resources are consumed/freed, and how.
All costs are fungible — freed resources can be redeployed to any purpose.

Costs are the MEANS side. Every hedonic end (HTC) is accessed through costs.
A person can't improve CONNECTION if their TIME, ATTENTION, and FINANCIAL
costs leave no resources for redeployment. Tools that modify costs unlock
access to ends.
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

# Full subcategory taxonomy — what each cost dimension contains
COST_SUBCATEGORIES = {
    "T": {
        "1": "Labor time (work performed for income)",
        "2": "Activity duration (time to accomplish the thing)",
        "3": "Preparation / setup time",
        "4": "Coordination / scheduling / arranging",
        "5": "Travel / transit (instrumental movement)",
        "6": "Maintenance / upkeep",
        "7": "Learning curve / skill acquisition",
        "8": "Recovery / cleanup",
        "9": "Waiting / queuing",
    },
    "F": {
        "1": "Direct expenditure",
        "2": "Indirect / overhead",
        "3": "Depreciation / replacement cycle",
        "4": "Insurance / risk premium",
        "5": "Tax / regulatory levy",
    },
    "A": {
        "1": "Cognitive load (decisions, focus)",
        "2": "Uncertainty / ambiguity borne",
        "3": "Information gathering (research, comparison)",
        "4": "Monitoring / vigilance",
    },
    "P": {
        "1": "Bodily effort / exertion",
        "2": "Discomfort / pain",
        "3": "Health risk exposure",
        "4": "Sensory burden (noise, heat, crowding)",
    },
    "S": {
        "1": "Labor extracted from others",
        "2": "Relationship capital spent",
        "3": "Status / reputation risk",
        "4": "Privacy surrendered",
        "5": "Obligation / reciprocity incurred",
    },
    "E": {
        "1": "Carbon / emissions",
        "2": "Waste generated",
        "3": "Resource depletion",
    },
    "R": {
        "1": "Compliance burden",
        "2": "Liability exposure",
        "3": "Reporting / documentation",
    },
    "K": {
        "1": "Opacity cost (black-box decision-making)",
        "2": "Data sovereignty (who owns/sees the data)",
        "3": "Institutional knowledge loss",
        "4": "Accuracy risk (wrong answers with confidence)",
    },
    "X": {
        "1": "Signal acquisition (credentials, brands, markers)",
        "2": "Signal maintenance (ongoing performance, appearance)",
        "3": "Signal competition (zero-sum positioning)",
        "4": "Placebo investment (belief-generating expenditure)",
        "5": "Network access (entry to status-gated opportunities)",
    },
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
    subcategory: str = ""   # e.g., 1 (labor time), 1 (direct expenditure)
    description: str = ""
    modifier: HQCM = field(default_factory=HQCM)
    blocks_domain: str = ""  # Which HTC domain this cost blocks access to (e.g., "07")

    @property
    def code(self) -> str:
        if self.subcategory:
            return f"{self.category}.{self.subcategory}"
        return self.category

    @property
    def category_name(self) -> str:
        return COST_CATEGORIES.get(self.category, "UNKNOWN")

    @property
    def subcategory_name(self) -> str:
        subs = COST_SUBCATEGORIES.get(self.category, {})
        return subs.get(self.subcategory, "")

    def __str__(self) -> str:
        mods = self.modifier.to_dict()
        mod_str = f" {mods}" if mods else ""
        blocks = f" [blocks HTC {self.blocks_domain}]" if self.blocks_domain else ""
        return f"HQC {self.code} ({self.category_name}){mod_str}{blocks}"


def get_cost_subcategories(category: str) -> dict[str, str]:
    """Get all subcategories for a cost category."""
    return COST_SUBCATEGORIES.get(category, {})


def list_all_costs() -> list[dict]:
    """List all cost categories with their subcategories."""
    result = []
    for code, name in COST_CATEGORIES.items():
        subs = COST_SUBCATEGORIES.get(code, {})
        result.append({
            "code": code,
            "name": name,
            "subcategories": [
                {"code": f"{code}.{sub_code}", "description": desc}
                for sub_code, desc in subs.items()
            ],
        })
    return result
