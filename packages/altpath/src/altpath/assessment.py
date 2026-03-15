"""
Personal hedonic life assessment engine.

Score yourself across the 10 hedonic domains.
Identify gaps, strengths, and redeployment opportunities.
"""

from dataclasses import dataclass, field
from hedonics.taxonomy import DOMAINS, list_domains


@dataclass
class DomainScore:
    """A score for a single hedonic domain."""
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
class Assessment:
    """A complete hedonic life assessment across all 10 domains."""
    scores: dict[str, DomainScore] = field(default_factory=dict)

    def score_domain(self, code: str, score: float, notes: str = ""):
        domain = DOMAINS[code]
        self.scores[code] = DomainScore(
            domain_code=code,
            domain_name=domain.name,
            score=score,
            notes=notes,
        )

    def gaps(self, threshold: float = 5.0) -> list[DomainScore]:
        """Domains scoring below the threshold — where you need improvement."""
        return sorted(
            [s for s in self.scores.values() if s.score < threshold],
            key=lambda s: s.score,
        )

    def strengths(self, threshold: float = 7.0) -> list[DomainScore]:
        """Domains scoring above the threshold — where you're thriving."""
        return sorted(
            [s for s in self.scores.values() if s.score >= threshold],
            key=lambda s: -s.score,
        )

    def hedonic_index(self) -> float:
        """Overall hedonic index — average across all scored domains."""
        if not self.scores:
            return 0.0
        return sum(s.score for s in self.scores.values()) / len(self.scores)

    def unscored_domains(self) -> list[str]:
        """Domains not yet assessed."""
        return [
            f"{code} {d.name}"
            for code, d in DOMAINS.items()
            if code not in self.scores
        ]

    def to_dict(self) -> dict:
        return {
            "hedonic_index": round(self.hedonic_index(), 1),
            "scores": {
                code: {
                    "domain": s.domain_name,
                    "score": s.score,
                    "level": s.level,
                    "notes": s.notes,
                }
                for code, s in self.scores.items()
            },
            "gaps": [
                {"code": s.domain_code, "domain": s.domain_name, "score": s.score}
                for s in self.gaps()
            ],
            "strengths": [
                {"code": s.domain_code, "domain": s.domain_name, "score": s.score}
                for s in self.strengths()
            ],
            "unscored": self.unscored_domains(),
        }
