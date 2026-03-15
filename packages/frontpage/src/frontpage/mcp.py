"""
Front Page MCP Server — hedonically-optimized feed via any LLM.

Usage:
    python -m frontpage.mcp
    Add to Claude/GPT config:
    {"command": "python", "args": ["-m", "frontpage.mcp"]}
"""

from fastmcp import FastMCP
from frontpage.feed import (
    FeedItem, UserProfile, rank_feed, explain_ranking, CONTENT_TYPES,
)
from frontpage.sources import (
    SOURCE_REGISTRY, get_search_terms, get_key_datasets,
)
from hedonics.taxonomy import DOMAINS
from hedonics.hqc import COST_CATEGORIES
from hedonics.storage import (
    load_profile, save_feed_items, load_feed_items,
    save_grade, HedonicGrade,
)

mcp = FastMCP(
    name="Front Page",
    instructions=(
        "The front page of your hedonic life. A feed that surfaces news, "
        "research, tools, policies, and datasets based on YOUR assessed "
        "hedonic needs — not engagement metrics. "
        "Use the user's altpath profile (domain scores + cost burdens) to "
        "rank content by hedonic relevance. Prioritize content that "
        "unblocks deficient domains by reducing high-burden costs."
    ),
)

_profile = UserProfile()
_feed_items: list[FeedItem] = []


# === PROFILE ===

@mcp.tool
def set_profile(domain_scores: dict = None, cost_burdens: dict = None,
                cost_blocks: dict = None, interests: list[str] = None) -> dict:
    """Set or update your hedonic profile for feed personalization.

    Import from an altpath assessment, or set directly.

    Args:
        domain_scores: Dict of domain code → score (1-10).
                       E.g., {"01": 7, "02": 4, "07": 3, "08": 4}
        cost_burdens: Dict of cost category → burden (1-10).
                      E.g., {"T": 8, "F": 3, "A": 7}
        cost_blocks: Dict of cost category → list of blocked domains.
                     E.g., {"T": ["07", "08"], "A": ["06"]}
        interests: Additional interest tags for content matching.
    """
    global _profile
    if domain_scores:
        _profile.domain_scores = domain_scores
    if cost_burdens:
        _profile.cost_burdens = cost_burdens
    if cost_blocks:
        _profile.cost_blocks = cost_blocks
    if interests:
        _profile.interests = interests

    return {
        "profile_set": True,
        "gap_domains": _profile.gap_domains(),
        "heavy_costs": _profile.heavy_costs(),
        "blocking_costs": _profile.blocking_costs(),
        "feed_will_prioritize": [
            DOMAINS[d].name for d in _profile.gap_domains() if d in DOMAINS
        ],
    }


@mcp.tool
def get_profile() -> dict:
    """Get the current hedonic profile used for feed ranking."""
    return {
        "domain_scores": _profile.domain_scores,
        "cost_burdens": _profile.cost_burdens,
        "cost_blocks": _profile.cost_blocks,
        "interests": _profile.interests,
        "gap_domains": [
            {"code": d, "name": DOMAINS[d].name}
            for d in _profile.gap_domains() if d in DOMAINS
        ],
        "heavy_costs": [
            {"code": c, "name": COST_CATEGORIES.get(c, c)}
            for c in _profile.heavy_costs()
        ],
    }


# === FEED MANAGEMENT ===

@mcp.tool
def add_item(title: str, content_type: str = "news", url: str = "",
             source: str = "", summary: str = "",
             domains: list[str] = None, costs: list[str] = None,
             cost_direction: str = "", tags: list[str] = None) -> dict:
    """Add a content item to the feed for ranking.

    Tag it with hedonic domains (ENDS) and cost categories (MEANS) it addresses.
    The feed engine will score it against your profile.

    Args:
        title: Item title
        content_type: news | research | tool | policy | dataset | resource
        url: Link to the content
        source: Where it came from
        summary: Brief description
        domains: HTC domains this serves (e.g., ["07", "08"])
        costs: HQC costs this modifies (e.g., ["T", "F"])
        cost_direction: decreased | increased
        tags: Additional tags for matching
    """
    item = FeedItem(
        title=title,
        url=url,
        source=source,
        content_type=content_type,
        summary=summary,
        htc_domains=domains or [],
        hqc_costs=costs or [],
        cost_direction=cost_direction,
        tags=tags or [],
    )
    _feed_items.append(item)
    item.relevance_score = 0.0
    if _profile.domain_scores:
        from frontpage.feed import score_item
        item.relevance_score = score_item(item, _profile)

    return {
        "added": title,
        "relevance_score": round(item.relevance_score, 2),
        "total_items": len(_feed_items),
    }


@mcp.tool
def get_feed(limit: int = 10) -> list[dict]:
    """Get your personalized hedonic feed, ranked by relevance to your profile.

    Items that unblock your deficient domains rank highest.
    Items that reduce your heavy cost burdens rank next.
    Items matching your gap domains rank after that."""
    if not _profile.domain_scores:
        return [{"note": "Set your profile first with set_profile() to get personalized ranking."}]

    ranked = rank_feed(_feed_items.copy(), _profile)
    results = []
    for item in ranked[:limit]:
        result = item.to_dict()
        result["why"] = explain_ranking(item, _profile)
        results.append(result)
    return results


# === DISCOVERY ===

@mcp.tool
def suggest_searches(max_per_domain: int = 3) -> list[dict]:
    """Suggest research search terms based on your gap domains.

    Uses your profile to find what academic research, datasets,
    and policy discussions are most relevant to YOUR hedonic gaps."""
    if not _profile.domain_scores:
        return [{"note": "Set your profile first to get personalized suggestions."}]

    suggestions = []
    for domain_code in _profile.gap_domains():
        if domain_code not in DOMAINS:
            continue
        domain = DOMAINS[domain_code]
        terms = get_search_terms(domain_code)
        datasets = get_key_datasets(domain_code)

        # Also suggest cost-reducer searches for blocking costs
        cost_searches = []
        for cost_cat, blocked in _profile.blocking_costs().items():
            if domain_code in blocked:
                cost_name = COST_CATEGORIES.get(cost_cat, cost_cat)
                cost_searches.append(f"reduce {cost_name.lower()} to improve {domain.name.lower()}")

        suggestions.append({
            "domain": {"code": domain_code, "name": domain.name},
            "research_terms": terms[:max_per_domain],
            "key_datasets": datasets[:max_per_domain],
            "cost_reducer_searches": cost_searches,
        })

    return suggestions


@mcp.tool
def load_my_profile() -> dict:
    """Load your altpath profile from shared storage (~/.hedonics/).
    Use this instead of set_profile() if you've already done an altpath assessment."""
    saved = load_profile()
    if not saved:
        return {"error": "No profile found in ~/.hedonics/. Run 'altpath assess' first."}

    global _profile
    _profile = UserProfile(
        domain_scores={e["code"]: e["score"] for e in saved.get("ends", [])},
        cost_burdens={m["code"]: m["burden"] for m in saved.get("means", [])},
        cost_blocks={m["code"]: m.get("blocks", []) for m in saved.get("means", []) if m.get("blocks")},
    )
    rerankFeed()
    return {
        "profile_loaded": True,
        "source": "~/.hedonics/profile/assessment.json",
        "gap_domains": [DOMAINS[d].name for d in _profile.gap_domains() if d in DOMAINS],
        "heavy_costs": [COST_CATEGORIES.get(c, c) for c in _profile.heavy_costs()],
    }


def rerankFeed():
    """Re-rank all feed items against the current profile."""
    if not _profile.domain_scores:
        return
    for item in _feed_items:
        from frontpage.feed import score_item
        item.relevance_score = score_item(item, _profile)


@mcp.tool
def save_my_feed() -> dict:
    """Save current feed items to shared storage (~/.hedonics/feed/).
    Items persist between sessions."""
    items = [item.to_dict() for item in _feed_items]
    path = save_feed_items(items)
    return {"saved": len(items), "path": str(path)}


@mcp.tool
def grade_item(title: str, purpose_score: float = 5.0,
               cost_efficiency: float = 5.0, notes: str = "") -> dict:
    """Grade a feed item on its hedonic value. Saves to shared grading storage.

    Args:
        title: Title of the feed item to grade
        purpose_score: 0-10, how well does it serve its purpose?
        cost_efficiency: 0-10, how efficiently does it modify costs?
        notes: Optional grading notes
    """
    item = next((i for i in _feed_items if i.title == title), None)
    if not item:
        return {"error": f"Item '{title}' not found in feed."}

    g = HedonicGrade(
        item_type="content",
        item_name=title,
        domains_served=item.htc_domains,
        costs_modified=item.hqc_costs,
        cost_effects={"direction": item.cost_direction} if item.cost_direction else {},
        purpose_score=purpose_score,
        cost_efficiency=cost_efficiency,
        relevance_score=item.relevance_score,
        notes=notes,
    )
    path = save_grade(g)
    return {**g.to_dict(), "saved_to": str(path)}


@mcp.tool
def content_types() -> list[dict]:
    """List all content types that can appear in the feed."""
    return [
        {"type": t, "description": SOURCE_REGISTRY.get(t, {}).get("description", "")}
        for t in CONTENT_TYPES
    ]


@mcp.tool
def available_sources() -> dict:
    """Show all content source registries and their connectors."""
    return SOURCE_REGISTRY


if __name__ == "__main__":
    mcp.run()
