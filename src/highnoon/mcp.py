"""
High Noon MCP Server — software purpose assessment via any LLM.

Usage:
    python -m highnoon.mcp
    Add to Claude/GPT config:
    {"command": "python", "args": ["-m", "highnoon.mcp"]}
"""

from fastmcp import FastMCP
from highnoon.assess import SoftwareAssessment, read_project_signals
from hedonics.taxonomy import DOMAINS

mcp = FastMCP(
    name="High Noon",
    instructions=(
        "Software purpose assessment tool. Analyze codebases and classify them "
        "by the human purposes they serve using the Hedonics taxonomy. "
        "Read project signals (README, config) and propose HTC classifications."
    ),
)

_assessments: dict[str, SoftwareAssessment] = {}


@mcp.tool
def scan(path: str = ".") -> dict:
    """Scan a project directory and extract signals (README, config, etc.)."""
    signals = read_project_signals(path)
    return {
        "name": signals.get("name", "unknown"),
        "path": signals.get("path", path),
        "has_readme": "readme" in signals,
        "has_pyproject": "pyproject" in signals,
        "has_package_json": "package_json" in signals,
        "readme_preview": signals.get("readme", "")[:500],
    }


@mcp.tool
def assess(path: str = ".", domain_code: str = "", activity: str = "",
           quality: dict = None, description: str = "") -> dict:
    """Add an HTC classification to a project's assessment.

    Args:
        path: Project directory path
        domain_code: Hedonic domain (01-10)
        activity: Sub-activity within the domain
        quality: Quality modifiers dict (e.g., {"fidelity": "high", "scope": "partial"})
        description: Human-readable description of the purpose
    """
    if path not in _assessments:
        signals = read_project_signals(path)
        _assessments[path] = SoftwareAssessment(
            project_path=signals.get("path", path),
            project_name=signals.get("name", "unknown"),
            method="llm-proposed",
        )
    _assessments[path].add_purpose(domain_code, activity, quality or {}, description)
    return _assessments[path].to_dict()


@mcp.tool
def add_cost(path: str = ".", category: str = "", subcategory: str = "",
             description: str = "", direction: str = "", magnitude: str = "",
             distribution: str = "") -> dict:
    """Add an HQC cost classification to a project's assessment.

    Args:
        path: Project directory path
        category: Cost category (T/F/A/P/S/E/R/K/X)
        subcategory: Sub-category (e.g., "1" for T.1)
        description: What cost is being modified
        direction: increased | decreased
        magnitude: marginal | moderate | significant | eliminated
        distribution: user | third-party | society
    """
    if path not in _assessments:
        signals = read_project_signals(path)
        _assessments[path] = SoftwareAssessment(
            project_path=signals.get("path", path),
            project_name=signals.get("name", "unknown"),
            method="llm-proposed",
        )
    _assessments[path].add_cost(
        category, subcategory, description,
        direction=direction, magnitude=magnitude, distribution=distribution,
    )
    return _assessments[path].to_dict()


@mcp.tool
def get_assessment(path: str = ".") -> dict:
    """Get the full assessment for a project."""
    if path in _assessments:
        return _assessments[path].to_dict()
    return {"error": f"No assessment found for {path}. Run 'scan' and 'assess' first."}


@mcp.tool
def list_assessments() -> list[dict]:
    """List all assessed projects in this session."""
    return [a.to_dict() for a in _assessments.values()]


if __name__ == "__main__":
    mcp.run()
