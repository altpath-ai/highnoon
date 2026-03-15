"""
Personal hedonic life assessment engine.

Score yourself across BOTH:
- ENDS: the 10 hedonic domains (what you value)
- MEANS: the 9 cost categories (what blocks or enables your access)

Many ends are locked behind means costs. The assessment identifies
not just WHERE you're deficient, but WHY — which costs are blocking
access to the hedonic domains you need.
"""

from dataclasses import dataclass, field
from hedonics.taxonomy import DOMAINS, list_domains
from hedonics.hqc import COST_CATEGORIES


@dataclass
class DomainScore:
    """A score for a single hedonic domain (END)."""
    domain_code: str
    domain_name: str
    score: float  # 1-10
    notes: str = ""

    @property
    def level(self) -> str:
        if self.score >= 8:
            return "thriving"
        elif self.score >= 5:
            return "adequate"
        elif self.score >= 3:
            return "deficient"
        else:
            return "critical"


@dataclass
class CostBurden:
    """A score for a single cost category (MEANS).
    High score = high burden = this cost is consuming your resources.
    Low score = low burden = this cost is well-managed."""
    category: str       # T, F, A, P, S, E, R, K, X
    category_name: str
    burden: float       # 1-10 (10 = crushing, 1 = negligible)
    notes: str = ""
    blocks_domains: list[str] = field(default_factory=list)  # which ends this cost blocks

    @property
    def level(self) -> str:
        if self.burden >= 8:
            return "crushing"
        elif self.burden >= 6:
            return "heavy"
        elif self.burden >= 4:
            return "moderate"
        else:
            return "manageable"


@dataclass
class Assessment:
    """A complete hedonic life assessment — ENDS and MEANS."""
    domain_scores: dict[str, DomainScore] = field(default_factory=dict)
    cost_burdens: dict[str, CostBurden] = field(default_factory=dict)

    # === ENDS ===

    def score_domain(self, code: str, score: float, notes: str = ""):
        """Score a hedonic domain (END). 1=critical, 10=thriving."""
        domain = DOMAINS[code]
        self.domain_scores[code] = DomainScore(
            domain_code=code,
            domain_name=domain.name,
            score=score,
            notes=notes,
        )

    def gaps(self, threshold: float = 5.0) -> list[DomainScore]:
        """Domains scoring below threshold — ends needing improvement."""
        return sorted(
            [s for s in self.domain_scores.values() if s.score < threshold],
            key=lambda s: s.score,
        )

    def strengths(self, threshold: float = 7.0) -> list[DomainScore]:
        """Domains scoring above threshold — ends where you're thriving."""
        return sorted(
            [s for s in self.domain_scores.values() if s.score >= threshold],
            key=lambda s: -s.score,
        )

    # === MEANS ===

    def score_cost(self, category: str, burden: float, notes: str = "",
                   blocks_domains: list[str] = None):
        """Score a cost burden (MEANS). 1=negligible, 10=crushing.
        Optionally specify which hedonic domains this cost blocks."""
        cat = category.upper()
        self.cost_burdens[cat] = CostBurden(
            category=cat,
            category_name=COST_CATEGORIES.get(cat, "UNKNOWN"),
            burden=burden,
            notes=notes,
            blocks_domains=blocks_domains or [],
        )

    def heavy_costs(self, threshold: float = 6.0) -> list[CostBurden]:
        """Costs with burden above threshold — means that are consuming too many resources."""
        return sorted(
            [c for c in self.cost_burdens.values() if c.burden >= threshold],
            key=lambda c: -c.burden,
        )

    def manageable_costs(self, threshold: float = 4.0) -> list[CostBurden]:
        """Costs with burden below threshold — means that are well-managed."""
        return sorted(
            [c for c in self.cost_burdens.values() if c.burden < threshold],
            key=lambda c: c.burden,
        )

    # === COMBINED ANALYSIS ===

    def blocked_ends(self) -> list[dict]:
        """Ends that are deficient AND have identified cost blockers.
        This is the actionable output: what you want AND what's stopping you."""
        blocked = []
        gap_codes = {s.domain_code for s in self.gaps()}
        for cost in self.heavy_costs():
            for domain_code in cost.blocks_domains:
                if domain_code in gap_codes:
                    domain = self.domain_scores[domain_code]
                    blocked.append({
                        "end": {
                            "code": domain.domain_code,
                            "domain": domain.domain_name,
                            "score": domain.score,
                            "level": domain.level,
                        },
                        "blocked_by": {
                            "cost": cost.category,
                            "name": cost.category_name,
                            "burden": cost.burden,
                            "level": cost.level,
                            "notes": cost.notes,
                        },
                        "action": f"Reduce {cost.category_name} burden to unlock {domain.domain_name}",
                    })
        return blocked

    def hedonic_index(self) -> float:
        """Overall hedonic index — average across all scored domains."""
        if not self.domain_scores:
            return 0.0
        return sum(s.score for s in self.domain_scores.values()) / len(self.domain_scores)

    def cost_index(self) -> float:
        """Overall cost burden index — average across all scored costs.
        Lower is better (less resource drain)."""
        if not self.cost_burdens:
            return 0.0
        return sum(c.burden for c in self.cost_burdens.values()) / len(self.cost_burdens)

    def net_hedonic(self) -> float:
        """Net hedonic score = hedonic index - cost index.
        Positive = more value than cost. Negative = costs exceed value."""
        return self.hedonic_index() - self.cost_index()

    def unscored_domains(self) -> list[str]:
        return [f"{code} {d.name}" for code, d in DOMAINS.items()
                if code not in self.domain_scores]

    def unscored_costs(self) -> list[str]:
        return [f"{code} {name}" for code, name in COST_CATEGORIES.items()
                if code not in self.cost_burdens]

    def to_dict(self) -> dict:
        return {
            "hedonic_index": round(self.hedonic_index(), 1),
            "cost_index": round(self.cost_index(), 1),
            "net_hedonic": round(self.net_hedonic(), 1),
            "ends": {
                code: {
                    "domain": s.domain_name,
                    "score": s.score,
                    "level": s.level,
                    "notes": s.notes,
                }
                for code, s in self.domain_scores.items()
            },
            "means": {
                cat: {
                    "category": c.category_name,
                    "burden": c.burden,
                    "level": c.level,
                    "notes": c.notes,
                    "blocks": c.blocks_domains,
                }
                for cat, c in self.cost_burdens.items()
            },
            "gaps": [
                {"code": s.domain_code, "domain": s.domain_name, "score": s.score}
                for s in self.gaps()
            ],
            "heavy_costs": [
                {"code": c.category, "name": c.category_name, "burden": c.burden, "blocks": c.blocks_domains}
                for c in self.heavy_costs()
            ],
            "blocked_ends": self.blocked_ends(),
            "unscored_domains": self.unscored_domains(),
            "unscored_costs": self.unscored_costs(),
        }
