"""
AltPath MCP Server — personal hedonic assessment via any LLM.

Usage:
    python -m altpath.mcp
    Add to Claude/GPT config:
    {"command": "python", "args": ["-m", "altpath.mcp"]}
"""

from fastmcp import FastMCP
from altpath.assessment import Assessment
from hedonics.taxonomy import list_domains

mcp = FastMCP(
    name="AltPath",
    instructions=(
        "Personal hedonic life assessment. Help the user evaluate their "
        "quality of life across 10 hedonic domains, identify gaps, and "
        "discover their optimal path. Be thoughtful and supportive."
    ),
)

# In-memory assessment for the session
_assessment = Assessment()


@mcp.tool
def list_life_domains() -> list[dict]:
    """Show all 10 hedonic life domains available for self-assessment."""
    return [
        {
            "code": d.code,
            "name": d.name,
            "description": d.description,
            "examples": d.examples,
        }
        for d in list_domains()
    ]


@mcp.tool
def score(domain_code: str, value: float, notes: str = "") -> dict:
    """Score a hedonic domain (1-10). E.g., score('07', 4, 'feeling isolated lately')."""
    if not 1 <= value <= 10:
        return {"error": "Score must be between 1 and 10"}
    _assessment.score_domain(domain_code, value, notes)
    s = _assessment.scores[domain_code]
    return {
        "domain": s.domain_name,
        "score": s.score,
        "level": s.level,
        "notes": s.notes,
    }


@mcp.tool
def gaps(threshold: float = 5.0) -> list[dict]:
    """Show domains where you're scoring below the threshold — areas needing attention."""
    return [
        {"code": s.domain_code, "domain": s.domain_name, "score": s.score, "level": s.level}
        for s in _assessment.gaps(threshold)
    ]


@mcp.tool
def strengths(threshold: float = 7.0) -> list[dict]:
    """Show domains where you're thriving."""
    return [
        {"code": s.domain_code, "domain": s.domain_name, "score": s.score, "level": s.level}
        for s in _assessment.strengths(threshold)
    ]


@mcp.tool
def hedonic_index() -> dict:
    """Get your overall Hedonic Index — average score across all assessed domains."""
    return {
        "hedonic_index": round(_assessment.hedonic_index(), 1),
        "domains_scored": len(_assessment.scores),
        "domains_remaining": _assessment.unscored_domains(),
    }


@mcp.tool
def full_assessment() -> dict:
    """Get the complete assessment with all scores, gaps, and strengths."""
    return _assessment.to_dict()


@mcp.tool
def reset() -> str:
    """Reset the assessment to start fresh."""
    global _assessment
    _assessment = Assessment()
    return "Assessment reset. Ready to begin."


if __name__ == "__main__":
    mcp.run()
