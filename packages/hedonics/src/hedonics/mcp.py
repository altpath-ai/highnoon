"""
Hedonics MCP Server — expose the classification system to any LLM.

Usage:
    python -m hedonics.mcp          # start MCP server (stdio)
    Add to Claude/GPT config:
    {"command": "python", "args": ["-m", "hedonics.mcp"]}
"""

from fastmcp import FastMCP
from hedonics.taxonomy import DOMAINS, get_domain, list_domains
from hedonics.htc import HTC, QUALITY_MODIFIERS
from hedonics.hqc import COST_CATEGORIES, COST_MODIFIERS

mcp = FastMCP(
    name="Hedonics",
    instructions=(
        "Human Hedonics Teleology Classification System. "
        "Use these tools to classify purposes, search domains, "
        "and understand the hedonic taxonomy."
    ),
)


@mcp.tool
def domains() -> list[dict]:
    """List all 10 hedonic life domains with descriptions and examples."""
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
def domain(code: str) -> dict:
    """Get details for a specific hedonic domain by code (01-10) or name (e.g., CONNECTION)."""
    d = get_domain(code)
    return {
        "code": d.code,
        "name": d.name,
        "description": d.description,
        "examples": d.examples,
        "atus_mapping": d.atus_mapping,
        "mit_mapping": d.mit_mapping,
    }


@mcp.tool
def classify(description: str) -> list[dict]:
    """Classify a purpose description into suggested HTC domain codes.

    Provide a natural language description of what something does for humans,
    and get back suggested hedonic domain classifications.
    """
    description_lower = description.lower()
    matches = []
    keywords = {
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
    for code, words in keywords.items():
        matched_words = [w for w in words if w in description_lower]
        if matched_words:
            d = DOMAINS[code]
            matches.append({
                "htc_code": code,
                "domain": d.name,
                "confidence": "suggested",
                "matched_keywords": matched_words,
                "description": d.description,
            })
    if not matches:
        matches.append({
            "htc_code": "??",
            "domain": "UNCLASSIFIED",
            "confidence": "none",
            "note": "No keyword matches found. Provide more detail about the human purpose served.",
        })
    return matches


@mcp.tool
def quality_modifiers() -> list[str]:
    """List all hedonic quality modifiers used to rate purpose fulfillment."""
    return QUALITY_MODIFIERS


@mcp.tool
def cost_categories() -> dict[str, str]:
    """List all 9 fungible cost categories (T, F, A, P, S, E, R, K, X)."""
    return COST_CATEGORIES


@mcp.tool
def cost_modifiers() -> list[str]:
    """List all cost modifier dimensions (direction, magnitude, distribution, etc.)."""
    return COST_MODIFIERS


@mcp.resource("hedonics://taxonomy")
def taxonomy_resource() -> str:
    """The full hedonic taxonomy as a reference document."""
    lines = ["# Hedonic Taxonomy — 10 Domains\n"]
    for d in list_domains():
        lines.append(f"## {d.code} {d.name}")
        lines.append(f"{d.description}\n")
        lines.append(f"Examples: {', '.join(d.examples)}\n")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
