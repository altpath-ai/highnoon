"""
AltPath MCP Server — personal hedonic assessment: ENDS and MEANS.

Usage:
    python -m altpath.mcp
    Add to Claude/GPT config:
    {"command": "python", "args": ["-m", "altpath.mcp"]}
"""

from fastmcp import FastMCP
from altpath.assessment import Assessment
from hedonics.taxonomy import list_domains
from hedonics.hqc import COST_CATEGORIES

mcp = FastMCP(
    name="AltPath",
    instructions=(
        "Personal hedonic life assessment. Help the user evaluate BOTH their "
        "hedonic ends (10 domains of intrinsic value) AND their cost burdens "
        "(9 categories of means/costs that block access to those ends). "
        "Identify not just WHERE they're deficient, but WHY — which costs "
        "are blocking access. Be thoughtful, supportive, and actionable."
    ),
)

_assessment = Assessment()


# === ENDS ===

@mcp.tool
def list_ends() -> list[dict]:
    """Show all 10 hedonic life domains (ENDS) available for self-assessment."""
    return [
        {"code": d.code, "name": d.name, "description": d.description,
         "examples": d.examples, "type": "END"}
        for d in list_domains()
    ]


@mcp.tool
def score_end(domain_code: str, value: float, notes: str = "") -> dict:
    """Score a hedonic domain (1=critical, 10=thriving).
    E.g., score_end('07', 4, 'feeling isolated lately')"""
    if not 1 <= value <= 10:
        return {"error": "Score must be between 1 and 10"}
    _assessment.score_domain(domain_code, value, notes)
    s = _assessment.domain_scores[domain_code]
    return {"domain": s.domain_name, "score": s.score, "level": s.level,
            "notes": s.notes, "type": "END"}


# === MEANS ===

@mcp.tool
def list_means() -> list[dict]:
    """Show all 9 fungible cost categories (MEANS) available for burden assessment."""
    return [
        {"code": code, "name": name, "type": "MEANS"}
        for code, name in COST_CATEGORIES.items()
    ]


@mcp.tool
def score_means(category: str, burden: float, notes: str = "",
                blocks_domains: list[str] = None) -> dict:
    """Score a cost burden (1=negligible, 10=crushing).
    Optionally specify which hedonic domains this cost blocks.
    E.g., score_means('T', 8, 'working 60hrs/week', blocks_domains=['07', '08'])"""
    if not 1 <= burden <= 10:
        return {"error": "Burden must be between 1 and 10"}
    _assessment.score_cost(category, burden, notes, blocks_domains or [])
    c = _assessment.cost_burdens[category.upper()]
    return {"category": c.category_name, "burden": c.burden, "level": c.level,
            "notes": c.notes, "blocks": c.blocks_domains, "type": "MEANS"}


# === ANALYSIS ===

@mcp.tool
def gaps(threshold: float = 5.0) -> list[dict]:
    """Show domains scoring below threshold — ENDS needing attention."""
    return [
        {"code": s.domain_code, "domain": s.domain_name, "score": s.score, "level": s.level}
        for s in _assessment.gaps(threshold)
    ]


@mcp.tool
def heavy_costs(threshold: float = 6.0) -> list[dict]:
    """Show costs with burden above threshold — MEANS consuming too many resources."""
    return [
        {"code": c.category, "name": c.category_name, "burden": c.burden,
         "level": c.level, "blocks": c.blocks_domains}
        for c in _assessment.heavy_costs(threshold)
    ]


@mcp.tool
def blocked_ends() -> list[dict]:
    """Show ends that are deficient AND have identified cost blockers.
    This is the KEY actionable output: what you WANT and what's STOPPING you.
    Returns pairs of (deficient end, blocking cost) with suggested action."""
    return _assessment.blocked_ends()


@mcp.tool
def hedonic_index() -> dict:
    """Get your Hedonic Index (ends), Cost Index (means), and Net Hedonic score."""
    return {
        "hedonic_index": round(_assessment.hedonic_index(), 1),
        "cost_index": round(_assessment.cost_index(), 1),
        "net_hedonic": round(_assessment.net_hedonic(), 1),
        "interpretation": (
            "positive = more hedonic value than cost burden, "
            "negative = costs exceed hedonic value, "
            "zero = breaking even"
        ),
        "domains_scored": len(_assessment.domain_scores),
        "costs_scored": len(_assessment.cost_burdens),
    }


@mcp.tool
def full_assessment() -> dict:
    """Get the complete assessment — all ends, means, gaps, heavy costs, and blocked ends."""
    return _assessment.to_dict()


@mcp.tool
def reset() -> str:
    """Reset the assessment to start fresh."""
    global _assessment
    _assessment = Assessment()
    return "Assessment reset. Ready to begin with both ENDS and MEANS."


if __name__ == "__main__":
    mcp.run()
