"""
Fungibility Calculus — the optimization engine of Teleological Hedonic Optimization.

All costs are fungible: time can become money, money can buy time,
attention can be traded for knowledge, status can reduce coordination costs.

This module computes:
1. Which means the person has in SURPLUS
2. Which means are BLOCKING their deficient ends
3. Which EXCHANGES between means would unlock the most hedonic value
4. Which TOOLS (tagged by highnoon) facilitate those exchanges

The core insight: you don't optimize ends directly.
You optimize the allocation of fungible means to unblock ends.
"""

from dataclasses import dataclass, field


# === Exchange Rate Matrix ===
# How efficiently can one cost type be converted to another?
# Scale: 0.0 (impossible) to 1.0 (perfect conversion)
# These are baseline rates — individual circumstances modify them.

EXCHANGE_RATES = {
    # FROM  → TO:  T     F     A     P     S     E     R     K     X
    "T": {"T": 1.0, "F": 0.8, "A": 0.3, "P": 0.2, "S": 0.5, "E": 0.1, "R": 0.1, "K": 0.6, "X": 0.4},
    "F": {"T": 0.7, "F": 1.0, "A": 0.4, "P": 0.5, "S": 0.3, "E": 0.3, "R": 0.5, "K": 0.5, "X": 0.6},
    "A": {"T": 0.2, "F": 0.3, "A": 1.0, "P": 0.1, "S": 0.4, "E": 0.1, "R": 0.2, "K": 0.7, "X": 0.3},
    "P": {"T": 0.3, "F": 0.4, "A": 0.2, "P": 1.0, "S": 0.2, "E": 0.1, "R": 0.1, "K": 0.2, "X": 0.3},
    "S": {"T": 0.4, "F": 0.3, "A": 0.5, "P": 0.2, "S": 1.0, "E": 0.1, "R": 0.2, "K": 0.4, "X": 0.7},
    "E": {"T": 0.1, "F": 0.2, "A": 0.1, "P": 0.1, "S": 0.1, "E": 1.0, "R": 0.3, "K": 0.1, "X": 0.1},
    "R": {"T": 0.1, "F": 0.3, "A": 0.2, "P": 0.1, "S": 0.1, "E": 0.2, "R": 1.0, "K": 0.3, "X": 0.2},
    "K": {"T": 0.5, "F": 0.6, "A": 0.6, "P": 0.1, "S": 0.3, "E": 0.2, "R": 0.3, "K": 1.0, "X": 0.5},
    "X": {"T": 0.3, "F": 0.5, "A": 0.3, "P": 0.1, "S": 0.7, "E": 0.1, "R": 0.2, "K": 0.4, "X": 1.0},
}

# Human-readable descriptions of key exchanges
EXCHANGE_DESCRIPTIONS = {
    ("T", "F"): "Trade time for money (labor → income)",
    ("F", "T"): "Buy time with money (hire help, outsource, automate)",
    ("T", "K"): "Trade time for knowledge (study, practice, learn)",
    ("K", "F"): "Trade knowledge for money (expertise → income)",
    ("K", "A"): "Knowledge reduces cognitive load (expertise makes things easier)",
    ("F", "P"): "Buy physical relief (gym, ergonomics, healthcare)",
    ("F", "A"): "Buy attention relief (hire assistant, automation tools)",
    ("S", "X"): "Trade social capital for status (networking → reputation)",
    ("X", "S"): "Trade status for social access (reputation opens doors)",
    ("X", "F"): "Trade status for money (reputation → premium pricing)",
    ("F", "X"): "Buy status signals (credentials, brands, markers)",
    ("T", "S"): "Trade time for social capital (invest in relationships)",
    ("F", "E"): "Pay for environmental sustainability (green premium)",
    ("K", "T"): "Knowledge saves time (expertise → efficiency)",
    ("F", "R"): "Pay for compliance (lawyers, accountants, consultants)",
    ("A", "K"): "Focused attention builds knowledge (deep work → learning)",
    ("T", "A"): "Rest recovers attention (sleep, breaks → cognitive capacity)",
    ("P", "F"): "Physical labor generates income (manual work)",
}


@dataclass
class CostProfile:
    """A person's cost profile — burden level for each means category."""
    burdens: dict[str, float] = field(default_factory=dict)  # category → burden (1-10)
    blocks: dict[str, list[str]] = field(default_factory=dict)  # category → blocked domains

    def surplus_categories(self, threshold: float = 4.0) -> list[str]:
        """Categories where burden is LOW = you have surplus resources here."""
        return [cat for cat, burden in self.burdens.items() if burden <= threshold]

    def deficit_categories(self, threshold: float = 6.0) -> list[str]:
        """Categories where burden is HIGH = you're resource-starved here."""
        return [cat for cat, burden in self.burdens.items() if burden >= threshold]

    def available_for_trade(self, threshold: float = 4.0) -> dict[str, float]:
        """How much surplus each category has available for exchange.
        Returns category → available_units (10 - burden = headroom)."""
        return {
            cat: round(10.0 - burden, 1)
            for cat, burden in self.burdens.items()
            if burden <= threshold
        }


@dataclass
class Exchange:
    """A recommended exchange between fungible cost types."""
    give: str           # Cost category to deploy (surplus)
    give_name: str
    receive: str        # Cost category to reduce (deficit)
    receive_name: str
    rate: float         # Exchange efficiency (0-1)
    description: str    # Human-readable description
    unlocks: list[str]  # Which hedonic domains this exchange could unblock
    priority: float     # Computed priority score

    def to_dict(self) -> dict:
        return {
            "exchange": f"{self.give} → {self.receive}",
            "give": {"code": self.give, "name": self.give_name},
            "receive": {"code": self.receive, "name": self.receive_name},
            "efficiency": self.rate,
            "description": self.description,
            "unlocks_domains": self.unlocks,
            "priority": round(self.priority, 2),
        }


def compute_exchanges(
    cost_profile: CostProfile,
    blocked_domains: dict[str, list[str]] = None,
    surplus_threshold: float = 4.0,
    deficit_threshold: float = 6.0,
    min_efficiency: float = 0.3,
) -> list[Exchange]:
    """Compute recommended fungible exchanges.

    Given a person's cost profile (what they have surplus of, what they're
    deficit in), compute which exchanges would unlock the most hedonic value.

    Args:
        cost_profile: The person's cost burdens
        blocked_domains: Map of cost category → list of hedonic domains it blocks
        surplus_threshold: Burden level below which = surplus
        deficit_threshold: Burden level above which = deficit
        min_efficiency: Minimum exchange rate to recommend

    Returns:
        Prioritized list of recommended exchanges
    """
    from hedonics.hqc import COST_CATEGORIES

    blocked_domains = blocked_domains or cost_profile.blocks
    surpluses = cost_profile.surplus_categories(surplus_threshold)
    deficits = cost_profile.deficit_categories(deficit_threshold)

    if not surpluses or not deficits:
        return []

    exchanges = []
    for give in surpluses:
        for receive in deficits:
            if give == receive:
                continue

            rate = EXCHANGE_RATES.get(give, {}).get(receive, 0.0)
            if rate < min_efficiency:
                continue

            # What domains would reducing this deficit unlock?
            unlocks = blocked_domains.get(receive, [])

            # Priority = exchange rate × deficit severity × number of domains unlocked
            deficit_severity = cost_profile.burdens.get(receive, 5.0) / 10.0
            domain_count = max(len(unlocks), 1)
            surplus_headroom = (10.0 - cost_profile.burdens.get(give, 5.0)) / 10.0
            priority = rate * deficit_severity * domain_count * surplus_headroom

            desc = EXCHANGE_DESCRIPTIONS.get(
                (give, receive),
                f"Convert {COST_CATEGORIES.get(give, give)} surplus to reduce {COST_CATEGORIES.get(receive, receive)} burden"
            )

            exchanges.append(Exchange(
                give=give,
                give_name=COST_CATEGORIES.get(give, give),
                receive=receive,
                receive_name=COST_CATEGORIES.get(receive, receive),
                rate=rate,
                description=desc,
                unlocks=unlocks,
                priority=priority,
            ))

    # Sort by priority (highest first)
    exchanges.sort(key=lambda e: -e.priority)
    return exchanges


def format_exchange_plan(exchanges: list[Exchange], max_recommendations: int = 5) -> str:
    """Format exchange recommendations as human-readable text."""
    if not exchanges:
        return "No viable exchanges found. Your cost profile may be balanced, or all exchange rates are below threshold."

    lines = ["\n  Fungibility Calculus — Recommended Exchanges:\n"]
    for i, ex in enumerate(exchanges[:max_recommendations], 1):
        lines.append(f"  {i}. {ex.give} ({ex.give_name}) → {ex.receive} ({ex.receive_name})")
        lines.append(f"     {ex.description}")
        lines.append(f"     Efficiency: {ex.rate:.0%} | Priority: {ex.priority:.2f}")
        if ex.unlocks:
            lines.append(f"     Unlocks: {', '.join(ex.unlocks)}")
        lines.append("")

    return "\n".join(lines)
