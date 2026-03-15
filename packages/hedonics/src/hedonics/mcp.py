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
