"""
Policy assessment engine.

Evaluates public policy through the hedonic framework:
- Which ENDS does this policy serve?
- Which MEANS/COSTS does it modify?
- Who bears the costs? Who receives the hedonic value?
- What is the population-weighted hedonic impact?
"""

from dataclasses import dataclass, field
from hedonics.taxonomy import DOMAINS
from hedonics.hqc import COST_CATEGORIES


@dataclass
class PolicyImpact:
    """Impact of a policy on a specific hedonic domain or cost category."""
    code: str               # HTC domain code or HQC cost code
    name: str
    impact_type: str        # "END" or "MEANS"
    direction: str          # "improved" | "worsened" | "unchanged" | "uncertain"
    magnitude: str          # "marginal" | "moderate" | "significant" | "transformative"
    affected_population: str = ""    # Who is affected
    affected_count: str = ""         # How many
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "type": self.impact_type,
            "direction": self.direction,
            "magnitude": self.magnitude,
            "affected_population": self.affected_population,
            "affected_count": self.affected_count,
            "notes": self.notes,
        }


@dataclass
class DistributionalEffect:
    """Who gains and who bears costs from a policy."""
    group: str              # e.g., "low-wage workers", "employers", "consumers"
    effect: str             # "gains hedonic value" | "bears increased cost" | "mixed"
    domains_affected: list[str] = field(default_factory=list)
    costs_affected: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "group": self.group,
            "effect": self.effect,
            "domains_affected": self.domains_affected,
            "costs_affected": self.costs_affected,
            "notes": self.notes,
        }


@dataclass
class PolicyAssessment:
    """Full hedonic assessment of a public policy."""
    policy_name: str = ""
    policy_description: str = ""
    jurisdiction: str = ""
    impacts: list[PolicyImpact] = field(default_factory=list)
    distributional: list[DistributionalEffect] = field(default_factory=list)
    net_hedonic_estimate: str = ""
    recommendations: list[str] = field(default_factory=list)

    def add_end_impact(self, domain_code: str, direction: str, magnitude: str,
                       affected_population: str = "", affected_count: str = "",
                       notes: str = ""):
        domain = DOMAINS.get(domain_code, None)
        name = domain.name if domain else "UNKNOWN"
        self.impacts.append(PolicyImpact(
            code=domain_code, name=name, impact_type="END",
            direction=direction, magnitude=magnitude,
            affected_population=affected_population,
            affected_count=affected_count, notes=notes,
        ))

    def add_means_impact(self, cost_category: str, direction: str, magnitude: str,
                         affected_population: str = "", affected_count: str = "",
                         notes: str = ""):
        name = COST_CATEGORIES.get(cost_category, "UNKNOWN")
        self.impacts.append(PolicyImpact(
            code=cost_category, name=name, impact_type="MEANS",
            direction=direction, magnitude=magnitude,
            affected_population=affected_population,
            affected_count=affected_count, notes=notes,
        ))

    def add_distributional_effect(self, group: str, effect: str,
                                   domains: list[str] = None,
                                   costs: list[str] = None,
                                   notes: str = ""):
        self.distributional.append(DistributionalEffect(
            group=group, effect=effect,
            domains_affected=domains or [],
            costs_affected=costs or [],
            notes=notes,
        ))

    def ends_improved(self) -> list[PolicyImpact]:
        return [i for i in self.impacts if i.impact_type == "END" and i.direction == "improved"]

    def ends_worsened(self) -> list[PolicyImpact]:
        return [i for i in self.impacts if i.impact_type == "END" and i.direction == "worsened"]

    def costs_decreased(self) -> list[PolicyImpact]:
        return [i for i in self.impacts if i.impact_type == "MEANS" and i.direction == "improved"]

    def costs_increased(self) -> list[PolicyImpact]:
        return [i for i in self.impacts if i.impact_type == "MEANS" and i.direction == "worsened"]

    def to_dict(self) -> dict:
        return {
            "policy": self.policy_name,
            "description": self.policy_description,
            "jurisdiction": self.jurisdiction,
            "ends_improved": [i.to_dict() for i in self.ends_improved()],
            "ends_worsened": [i.to_dict() for i in self.ends_worsened()],
            "costs_decreased": [i.to_dict() for i in self.costs_decreased()],
            "costs_increased": [i.to_dict() for i in self.costs_increased()],
            "distributional_effects": [d.to_dict() for d in self.distributional],
            "net_hedonic_estimate": self.net_hedonic_estimate,
            "recommendations": self.recommendations,
        }
