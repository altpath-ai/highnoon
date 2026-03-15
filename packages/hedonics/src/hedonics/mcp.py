"""
Hedonics MCP Server — expose ENDS and MEANS classification to any LLM.

Usage:
    python -m hedonics.mcp          # start MCP server (stdio)
    Add to Claude/GPT config:
    {"command": "python", "args": ["-m", "hedonics.mcp"]}
"""

from fastmcp import FastMCP
from hedonics.taxonomy import DOMAINS, get_domain, list_domains
from hedonics.htc import HTC, QUALITY_MODIFIERS
from hedonics.hqc import (
    COST_CATEGORIES, COST_SUBCATEGORIES, COST_MODIFIERS,
    list_all_costs, get_cost_subcategories,
)
from hedonics.fungibility import (
    CostProfile, compute_exchanges, EXCHANGE_RATES, EXCHANGE_DESCRIPTIONS,
)
from hedonics.storage import (
    save_grade, load_grade, list_grades, grade_summary,
    load_profile, HedonicGrade,
)
from hedonics.registry import (
    search as registry_search, search_by_need, search_cost_reducers,
    rebuild_index, registry_stats,
)

# Which costs typically block access to which domains
DOMAIN_BLOCKERS = {
    "01": [("F.1", "Can't afford quality food"), ("T.2", "No time to cook"), ("K.3", "Don't know nutrition basics")],
    "02": [("F.1", "Can't afford adequate housing"), ("T.6", "No time for home maintenance"), ("R.1", "Regulatory barriers")],
    "03": [("F.1", "Can't afford healthcare"), ("T.1", "Work leaves no time for exercise"), ("A.1", "Too stressed for wellness")],
    "04": [("T.1", "Work consumes caregiving time"), ("A.1", "Emotional exhaustion"), ("F.1", "Can't afford childcare support")],
    "05": [("F.1", "Can't afford to travel"), ("T.1", "No time off from work"), ("P.1", "Physical limitations")],
    "06": [("T.1", "Work leaves no learning time"), ("F.1", "Can't afford education"), ("A.1", "Cognitive overload"), ("T.7", "Steep learning curve")],
    "07": [("T.1", "Work consumes social time"), ("A.1", "Mentally exhausted"), ("X.1", "Status anxiety"), ("P.4", "Sensory overload")],
    "08": [("T.1", "No leisure time"), ("F.1", "Can't afford recreation"), ("A.1", "Too drained for play"), ("P.2", "Physical pain")],
    "09": [("T.1", "No time to create"), ("A.1", "No creative bandwidth"), ("K.1", "Don't know where to start"), ("X.3", "Fear of judgment")],
    "10": [("T.1", "Survival mode — no reflection time"), ("A.2", "Uncertainty blocks meaning-making"), ("S.2", "No community")],
}

mcp = FastMCP(
    name="Hedonics",
    instructions=(
        "Human Hedonics Teleology Classification System. "
        "Classifies both ENDS (hedonic domains — what humans value) "
        "and MEANS (fungible costs — what blocks or enables access to those ends). "
        "Many hedonic ends are locked behind means costs. Tools that reduce costs "
        "unlock access to ends."
    ),
)


# === ENDS (Hedonic Domains) ===

@mcp.tool
def domains() -> list[dict]:
    """List all 10 hedonic life domains (ENDS) with descriptions and examples."""
    return [
        {
            "code": d.code,
            "name": d.name,
            "description": d.description,
            "examples": d.examples,
            "type": "END",
        }
        for d in list_domains()
    ]


@mcp.tool
def domain(code: str) -> dict:
    """Get details for a specific hedonic domain by code (01-10) or name (e.g., CONNECTION).
    Includes the cost blockers that typically prevent access to this end."""
    d = get_domain(code)
    blockers = DOMAIN_BLOCKERS.get(d.code, [])
    return {
        "code": d.code,
        "name": d.name,
        "description": d.description,
        "examples": d.examples,
        "atus_mapping": d.atus_mapping,
        "mit_mapping": d.mit_mapping,
        "type": "END",
        "cost_blockers": [
            {"cost_code": c, "description": desc}
            for c, desc in blockers
        ],
    }


# === MEANS (Costs) ===

@mcp.tool
def costs() -> list[dict]:
    """List all 9 fungible cost categories (MEANS) with full subcategories.
    These are the resources consumed/freed that enable or block access to hedonic ends."""
    return list_all_costs()


@mcp.tool
def cost(category: str) -> dict:
    """Get subcategories for a specific cost category (e.g., 'T' for TIME, 'X' for STATUS)."""
    cat = category.upper()
    if cat not in COST_CATEGORIES:
        return {"error": f"Unknown category: {cat}. Valid: {list(COST_CATEGORIES.keys())}"}
    subs = get_cost_subcategories(cat)
    return {
        "code": cat,
        "name": COST_CATEGORIES[cat],
        "type": "MEANS",
        "subcategories": [
            {"code": f"{cat}.{sub_code}", "description": desc}
            for sub_code, desc in subs.items()
        ],
    }


@mcp.tool
def blockers(domain_code: str) -> dict:
    """Show the typical costs (MEANS) that block access to a hedonic domain (END).
    Use this to understand WHY someone can't improve in a domain and what costs
    need to be reduced to unlock it."""
    if domain_code not in DOMAINS:
        return {"error": f"Unknown domain: {domain_code}. Valid: 01-10"}
    d = DOMAINS[domain_code]
    domain_blockers = DOMAIN_BLOCKERS.get(domain_code, [])
    return {
        "domain_code": d.code,
        "domain_name": d.name,
        "description": d.description,
        "blockers": [
            {"cost_code": c, "description": desc}
            for c, desc in domain_blockers
        ],
        "guidance": f"Tools that DECREASE these costs unlock access to {d.name}. "
                    f"Search for software classified as reducing these specific HQC codes.",
    }


# === CLASSIFICATION (both ends and means) ===

@mcp.tool
def classify(description: str) -> dict:
    """Classify a description into BOTH ends served (HTC domains) and means modified (HQC costs).

    Provide a natural language description of what something does for humans,
    and get back suggested classifications for both the purposes served AND the costs modified.
    """
    description_lower = description.lower()

    end_keywords = {
        "01": ["food", "eat", "meal", "cook", "nourish", "nutrition", "diet", "drink"],
        "02": ["home", "house", "shelter", "sleep", "rest", "comfort", "safe", "housing"],
        "03": ["health", "medical", "wellness", "exercise", "fitness", "vitality", "therapy"],
        "04": ["care", "child", "parent", "nurtur", "elder", "family", "love", "bond"],
        "05": ["travel", "transport", "move", "explor", "trip", "journey", "drive", "commut"],
        "06": ["learn", "educat", "skill", "grow", "study", "knowledge", "master", "course"],
        "07": ["connect", "social", "communit", "friend", "relationship", "belong", "chat", "message"],
        "08": ["play", "game", "fun", "entertain", "recreation", "leisure", "music", "art", "sport"],
        "09": ["create", "make", "build", "write", "design", "express", "craft", "paint"],
        "10": ["meaning", "purpose", "spirit", "identity", "legacy", "volunteer", "faith", "reflect"],
    }

    means_keywords = {
        "T": ["time", "hour", "minutes", "schedule", "wait", "fast", "slow", "quick", "efficient", "automate"],
        "F": ["cost", "price", "money", "afford", "cheap", "expensive", "budget", "save", "free", "pay"],
        "A": ["attention", "focus", "cognitive", "distract", "overwhelm", "simple", "easy", "complex", "confus"],
        "P": ["effort", "physical", "pain", "comfort", "exert", "exhaust", "energy", "fatigue"],
        "S": ["privacy", "relationship", "reputation", "trust", "obligation"],
        "E": ["carbon", "emission", "waste", "environment", "sustain", "green", "eco"],
        "R": ["compliance", "regulation", "legal", "license", "audit", "liability"],
        "K": ["uncertain", "ambiguous", "opaque", "transparent", "understand", "clarity", "risk"],
        "X": ["status", "credential", "prestige", "signal", "brand"],
    }

    ends = []
    for code, words in end_keywords.items():
        matched = [w for w in words if w in description_lower]
        if matched:
            d = DOMAINS[code]
            ends.append({
                "htc_code": code,
                "domain": d.name,
                "type": "END",
                "matched_keywords": matched,
            })

    means = []
    for code, words in means_keywords.items():
        matched = [w for w in words if w in description_lower]
        if matched:
            means.append({
                "hqc_code": code,
                "category": COST_CATEGORIES[code],
                "type": "MEANS",
                "matched_keywords": matched,
            })

    return {
        "ends_served": ends or [{"note": "No end-domain matches. Describe the human purpose more specifically."}],
        "means_modified": means or [{"note": "No cost matches. Describe what costs are reduced/increased."}],
    }


@mcp.tool
def quality_modifiers() -> list[str]:
    """List all hedonic quality modifiers used to rate purpose fulfillment (ENDS side)."""
    return QUALITY_MODIFIERS


@mcp.tool
def cost_modifiers() -> list[str]:
    """List all cost modifier dimensions (MEANS side): direction, magnitude, distribution, etc."""
    return COST_MODIFIERS


# === FUNGIBILITY CALCULUS ===

@mcp.tool
def optimize(burdens: dict, blocked_by: dict = None) -> dict:
    """Run the fungibility calculus on a cost profile.

    Given a person's cost burdens, compute which exchanges between
    fungible means would unlock the most hedonic value.

    Args:
        burdens: Dict of cost category → burden score (1-10).
                 E.g., {"T": 8, "F": 3, "A": 7, "K": 2, "X": 4}
        blocked_by: Optional dict of cost category → list of hedonic domain codes it blocks.
                    E.g., {"T": ["07", "08"], "A": ["06", "09"]}

    Returns:
        Prioritized list of recommended exchanges with efficiency rates.

    Example:
        optimize(
            burdens={"T": 8, "F": 3, "A": 7, "K": 2},
            blocked_by={"T": ["07", "08"], "A": ["06"]}
        )
        → "K → A (Knowledge reduces cognitive load, efficiency 70%, unlocks GROWTH)"
        → "F → T (Buy time with money, efficiency 70%, unlocks CONNECTION, RECREATION)"
    """
    profile = CostProfile(
        burdens=burdens,
        blocks=blocked_by or {},
    )
    exchanges = compute_exchanges(profile)
    return {
        "surpluses": profile.surplus_categories(),
        "deficits": profile.deficit_categories(),
        "available_for_trade": profile.available_for_trade(),
        "recommendations": [ex.to_dict() for ex in exchanges[:7]],
        "total_exchanges_found": len(exchanges),
    }


@mcp.tool
def exchange_rate(give: str, receive: str) -> dict:
    """Look up the exchange rate between two cost types.

    How efficiently can you convert surplus in one cost type
    to reduce burden in another?

    Args:
        give: Cost category you have surplus of (T, F, A, P, S, E, R, K, X)
        receive: Cost category you need to reduce

    Returns:
        Exchange rate (0-1), description, and interpretation.
    """
    give = give.upper()
    receive = receive.upper()
    rate = EXCHANGE_RATES.get(give, {}).get(receive, 0.0)
    desc = EXCHANGE_DESCRIPTIONS.get(
        (give, receive),
        f"Convert {COST_CATEGORIES.get(give, give)} to reduce {COST_CATEGORIES.get(receive, receive)}"
    )
    if rate >= 0.7:
        interpretation = "Highly efficient exchange — strong conversion path"
    elif rate >= 0.4:
        interpretation = "Moderate efficiency — viable but with some friction"
    elif rate >= 0.2:
        interpretation = "Low efficiency — possible but costly conversion"
    else:
        interpretation = "Near-impossible exchange — these resources don't convert well"
    return {
        "give": {"code": give, "name": COST_CATEGORIES.get(give, give)},
        "receive": {"code": receive, "name": COST_CATEGORIES.get(receive, receive)},
        "rate": rate,
        "description": desc,
        "interpretation": interpretation,
    }


# === GRADING ===

@mcp.tool
def grade(item_name: str, item_type: str, domains_served: list[str] = None,
          costs_modified: list[str] = None, cost_effects: dict = None,
          purpose_score: float = 5.0, cost_efficiency: float = 5.0,
          notes: str = "") -> dict:
    """Grade any item (software, policy, or content) on its hedonic value.

    Assigns a letter grade (A+ through F) based on:
    - purpose_score: How well does it serve its declared hedonic purpose? (0-10)
    - cost_efficiency: How efficiently does it modify costs? (0-10)
    - relevance_score: Auto-computed from your altpath profile

    Args:
        item_name: Name of the thing being graded
        item_type: "software" | "policy" | "content"
        domains_served: HTC domains it serves (e.g., ["03", "07"])
        costs_modified: HQC costs it modifies (e.g., ["A", "T"])
        cost_effects: Dict of cost → {direction, magnitude}
        purpose_score: 0-10 rating of purpose fulfillment
        cost_efficiency: 0-10 rating of cost modification efficiency
        notes: Grading notes
    """
    # Compute relevance from profile
    relevance = 0.0
    user_profile = load_profile()
    if user_profile:
        gaps = {e["code"] for e in user_profile.get("ends", []) if e["score"] < 5}
        heavy = {m["code"] for m in user_profile.get("means", []) if m["burden"] >= 6}
        for d in (domains_served or []):
            if d in gaps:
                relevance += 3.0
        for c in (costs_modified or []):
            if c in heavy:
                relevance += 2.0
        relevance = min(relevance, 10.0)

    g = HedonicGrade(
        item_type=item_type,
        item_name=item_name,
        domains_served=domains_served or [],
        domain_quality={},
        costs_modified=costs_modified or [],
        cost_effects=cost_effects or {},
        purpose_score=purpose_score,
        cost_efficiency=cost_efficiency,
        relevance_score=relevance,
        notes=notes,
    )
    path = save_grade(g)
    return {**g.to_dict(), "saved_to": str(path)}


@mcp.tool
def get_grade(item_type: str, item_name: str) -> dict:
    """Look up a previously saved hedonic grade."""
    result = load_grade(item_type, item_name)
    if result:
        return result
    return {"error": f"No grade found for {item_type}/{item_name}"}


@mcp.tool
def all_grades(item_type: str = None) -> list[dict]:
    """List all hedonic grades, optionally filtered by type (software/policy/content)."""
    return list_grades(item_type)


@mcp.tool
def grades_dashboard() -> dict:
    """Summary of all grades across types — counts and grade distribution."""
    return grade_summary()


# === REGISTRY ===

@mcp.tool
def search(query: str = "", domains: list[str] = None, costs: list[str] = None,
           grade: str = "", item_type: str = "", cost_direction: str = "decreased") -> list[dict]:
    """Search the hedonic registry for tools, policies, or content.

    Examples:
        search(query="serves-health reduces-attention")
        search(domains=["03"], costs=["A"])
        search(grade="B", item_type="software")
        search(query="meditation")

    Args:
        query: Free-text search across tags, names, notes
        domains: Filter by HTC domains (e.g., ["03", "07"])
        costs: Filter by HQC costs modified (e.g., ["A", "T"])
        grade: Minimum grade (e.g., "B" matches B, B+, A, A+)
        item_type: "software" | "policy" | "content"
        cost_direction: "decreased" (default) or "increased"
    """
    return registry_search(
        query=query, domains=domains, costs=costs,
        grade=grade, item_type=item_type, cost_direction=cost_direction,
    )


@mcp.tool
def find_for_need(domain_code: str) -> list[dict]:
    """Find everything in the registry that serves a specific hedonic need.
    E.g., find_for_need("03") → all tools/policies/content that serve HEALTH."""
    domain = DOMAINS.get(domain_code)
    name = domain.name if domain else domain_code
    results = search_by_need(domain_code)
    return {
        "domain": name,
        "query": f"serves {name}, reduces costs",
        "results": results,
        "count": len(results),
    }


@mcp.tool
def find_cost_reducers(cost_code: str) -> list[dict]:
    """Find everything that reduces a specific cost.
    E.g., find_cost_reducers("A") → all tools that reduce ATTENTION burden."""
    cost_name = COST_CATEGORIES.get(cost_code, cost_code)
    results = search_cost_reducers(cost_code)
    return {
        "cost": cost_name,
        "query": f"reduces {cost_name} cost",
        "results": results,
        "count": len(results),
    }


@mcp.tool
def registry() -> dict:
    """Show registry statistics — what's indexed, coverage across domains and costs."""
    rebuild_index()
    return registry_stats()


@mcp.tool
def exchange_matrix() -> dict:
    """Show the full exchange rate matrix between all 9 cost types.
    Useful for understanding which resource conversions are efficient."""
    cats = list(COST_CATEGORIES.keys())
    return {
        "categories": {k: v for k, v in COST_CATEGORIES.items()},
        "matrix": {
            give: {receive: EXCHANGE_RATES[give][receive] for receive in cats}
            for give in cats
        },
        "reading": "Row = what you GIVE. Column = what you RECEIVE. Value = conversion efficiency (0-1).",
    }


# === RESOURCES ===

@mcp.resource("hedonics://taxonomy")
def taxonomy_resource() -> str:
    """The full hedonic taxonomy — ENDS and MEANS — as a reference document."""
    lines = ["# Hedonic Taxonomy\n"]
    lines.append("## ENDS — 10 Hedonic Domains (intrinsic value)\n")
    for d in list_domains():
        lines.append(f"### {d.code} {d.name}")
        lines.append(f"{d.description}")
        lines.append(f"Examples: {', '.join(d.examples)}\n")

    lines.append("\n## MEANS — 9 Fungible Cost Categories (instrumental)\n")
    for cost in list_all_costs():
        lines.append(f"### {cost['code']} {cost['name']}")
        for sub in cost["subcategories"]:
            lines.append(f"  {sub['code']}  {sub['description']}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
