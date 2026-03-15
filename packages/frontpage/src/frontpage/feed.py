"""
Hedonic feed engine.

Scores and ranks content by hedonic relevance to the user's assessed profile.
Content is tagged with HTC domains and HQC cost categories, then ranked by:
1. Which domains the user is deficient in (from altpath)
2. Which costs are blocking those domains (from altpath)
3. Whether the content helps reduce those blockers
4. Content type (research, tool, policy, dataset, news)
"""

from dataclasses import dataclass, field
from datetime import datetime
from hedonics.taxonomy import DOMAINS
from hedonics.hqc import COST_CATEGORIES


CONTENT_TYPES = [
    "news",         # News stories relevant to hedonic domains
    "research",     # Academic research, studies, papers
    "tool",         # Software tools tagged by highnoon
    "policy",       # Public policies assessed by mainstreet
    "dataset",      # Open datasets relevant to hedonic measurement
    "resource",     # Guides, courses, communities, services
]


@dataclass
class FeedItem:
    """A single item in the hedonic feed."""
    title: str
    url: str = ""
    source: str = ""
    content_type: str = "news"      # news | research | tool | policy | dataset | resource
    summary: str = ""
    htc_domains: list[str] = field(default_factory=list)    # Which ends this serves
    hqc_costs: list[str] = field(default_factory=list)      # Which costs this modifies
    cost_direction: str = ""        # decreased | increased (how it modifies costs)
    relevance_score: float = 0.0    # Computed based on user's profile
    published: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "type": self.content_type,
            "summary": self.summary,
            "domains": self.htc_domains,
            "costs_modified": self.hqc_costs,
            "cost_direction": self.cost_direction,
            "relevance_score": round(self.relevance_score, 2),
            "published": self.published,
            "tags": self.tags,
        }


@dataclass
class UserProfile:
    """User's hedonic profile for feed personalization."""
    domain_scores: dict[str, float] = field(default_factory=dict)   # domain → score (1-10)
    cost_burdens: dict[str, float] = field(default_factory=dict)    # cost cat → burden (1-10)
    cost_blocks: dict[str, list[str]] = field(default_factory=dict) # cost cat → blocked domains
    interests: list[str] = field(default_factory=list)              # Additional interest tags

    def gap_domains(self, threshold: float = 5.0) -> list[str]:
        """Domains below threshold — feed should prioritize these."""
        return [code for code, score in self.domain_scores.items()
                if score < threshold]

    def heavy_costs(self, threshold: float = 6.0) -> list[str]:
        """High-burden costs — feed should surface cost-reducers for these."""
        return [cat for cat, burden in self.cost_burdens.items()
                if burden >= threshold]

    def blocking_costs(self) -> dict[str, list[str]]:
        """Costs that block gap domains — highest priority for feed."""
        gaps = set(self.gap_domains())
        blocking = {}
        for cat, blocked in self.cost_blocks.items():
            relevant = [d for d in blocked if d in gaps]
            if relevant and cat in self.heavy_costs():
                blocking[cat] = relevant
        return blocking


def score_item(item: FeedItem, profile: UserProfile) -> float:
    """Score a feed item's relevance to the user's hedonic profile.

    Scoring priorities:
    1. Content that addresses BLOCKED ENDS gets highest score
    2. Content that reduces HIGH-BURDEN COSTS gets next highest
    3. Content that serves GAP DOMAINS gets base relevance
    4. Content matching user interests gets a bonus
    """
    score = 0.0

    gap_domains = set(profile.gap_domains())
    heavy_costs = set(profile.heavy_costs())
    blocking = profile.blocking_costs()

    # Tier 1: Addresses blocked ends (domain deficient AND cost blocking it)
    for domain in item.htc_domains:
        if domain in gap_domains:
            # Check if item also reduces the blocking cost
            for cost_cat in item.hqc_costs:
                if cost_cat in blocking:
                    blocked_domains = blocking[cost_cat]
                    if domain in blocked_domains and item.cost_direction == "decreased":
                        score += 10.0  # Highest priority: unblocks a blocked end

    # Tier 2: Reduces high-burden costs
    for cost_cat in item.hqc_costs:
        if cost_cat in heavy_costs and item.cost_direction == "decreased":
            score += 5.0

    # Tier 3: Serves gap domains
    for domain in item.htc_domains:
        if domain in gap_domains:
            score += 3.0

    # Tier 4: Matches interests
    for tag in item.tags:
        if tag in profile.interests:
            score += 1.0

    # Content type bonus (actionable content ranks higher)
    type_bonus = {
        "tool": 2.0,        # Immediately usable
        "resource": 1.5,    # Actionable
        "policy": 1.5,      # Systemic impact
        "research": 1.0,    # Knowledge
        "dataset": 0.5,     # Raw material
        "news": 0.5,        # Awareness
    }
    score += type_bonus.get(item.content_type, 0.0)

    return score


def rank_feed(items: list[FeedItem], profile: UserProfile) -> list[FeedItem]:
    """Rank feed items by hedonic relevance to the user's profile."""
    for item in items:
        item.relevance_score = score_item(item, profile)
    return sorted(items, key=lambda i: -i.relevance_score)


def explain_ranking(item: FeedItem, profile: UserProfile) -> str:
    """Explain WHY an item ranked the way it did."""
    reasons = []
    gap_domains = set(profile.gap_domains())
    heavy_costs = set(profile.heavy_costs())
    blocking = profile.blocking_costs()

    for domain in item.htc_domains:
        if domain in gap_domains:
            domain_name = DOMAINS.get(domain, None)
            name = domain_name.name if domain_name else domain
            for cost_cat in item.hqc_costs:
                if cost_cat in blocking and domain in blocking.get(cost_cat, []):
                    cost_name = COST_CATEGORIES.get(cost_cat, cost_cat)
                    reasons.append(
                        f"Unblocks {name} by reducing {cost_name} burden"
                    )
            if not any("Unblocks" in r for r in reasons):
                reasons.append(f"Serves {name} (your gap domain)")

    for cost_cat in item.hqc_costs:
        if cost_cat in heavy_costs and item.cost_direction == "decreased":
            cost_name = COST_CATEGORIES.get(cost_cat, cost_cat)
            if not any(cost_name in r for r in reasons):
                reasons.append(f"Reduces {cost_name} burden")

    if not reasons:
        reasons.append("General relevance")

    return "; ".join(reasons)
