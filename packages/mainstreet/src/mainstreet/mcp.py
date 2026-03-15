"""
Main Street MCP Server — public policy hedonic assessment via any LLM.

Usage:
    python -m mainstreet.mcp
    Add to Claude/GPT config:
    {"command": "python", "args": ["-m", "mainstreet.mcp"]}
"""

from fastmcp import FastMCP
from mainstreet.datasources import (
    fetch_bls_series, get_atus_profile, BLS_SERIES, ATUS_EMPLOYED_AVERAGES,
)
from mainstreet.policy import PolicyAssessment
from hedonics.taxonomy import DOMAINS
from hedonics.hqc import COST_CATEGORIES
from hedonics.storage import save_policy_assessment, load_policy_assessment, list_policy_assessments

mcp = FastMCP(
    name="Main Street",
    instructions=(
        "Public policy hedonic assessment tool. Use real federal data "
        "(BLS, MIT Living Wage, Census) to evaluate whether policies serve "
        "Main Street's hedonic needs. Assess which ENDS a policy improves, "
        "which MEANS/COSTS it modifies, and who bears the distributional effects. "
        "Be rigorous, data-driven, and clear about assumptions."
    ),
)

_assessments: dict[str, PolicyAssessment] = {}


# === DATA TOOLS ===

@mcp.tool
def bls_data(series: str = "cpi_all", start_year: int = 2024,
             end_year: int = 2025) -> dict:
    """Fetch real BLS data for a named series.

    Available series: cpi_all, cpi_food, cpi_housing, cpi_medical,
    cpi_transport, cpi_education, cpi_recreation, cpi_apparel,
    avg_hourly_earnings, avg_weekly_hours, unemployment_rate

    Or pass a raw BLS series ID directly."""
    series_id = BLS_SERIES.get(series, series)
    result = fetch_bls_series([series_id], start_year, end_year)
    if "error" in result:
        return result
    return {
        "series": series,
        "series_id": series_id,
        "data": result.get(series_id, []),
    }


@mcp.tool
def time_budget(employed: bool = True) -> dict:
    """Get the national ATUS time budget showing how Americans spend their day.

    Maps each activity to the hedonic framework:
    - MEANS (costs): working, commuting, housework, shopping
    - ENDS (purposes): leisure, eating, caring for family
    - PROCESSING: sleep, personal care

    Shows what % of the day goes to means vs. ends vs. processing."""
    return get_atus_profile(employed)


@mcp.tool
def hedonic_domains_mapped() -> list[dict]:
    """Show all 10 hedonic domains with their data source mappings.
    Which federal datasets measure each domain?"""
    mappings = {
        "01": {"bls_series": "cpi_food", "mit_category": "Food", "census_table": "S2201 (Food Stamps)"},
        "02": {"bls_series": "cpi_housing", "mit_category": "Housing", "census_table": "DP04 (Housing)"},
        "03": {"bls_series": "cpi_medical", "mit_category": "Healthcare", "census_table": "S2701 (Insurance)"},
        "04": {"bls_series": None, "mit_category": "Childcare", "census_table": None},
        "05": {"bls_series": "cpi_transport", "mit_category": "Transportation", "census_table": "S0801 (Commuting)"},
        "06": {"bls_series": "cpi_education", "mit_category": "Civic Engagement", "census_table": "S1501 (Education)"},
        "07": {"bls_series": None, "mit_category": "Internet & Communication", "census_table": "S2801 (Internet)"},
        "08": {"bls_series": "cpi_recreation", "mit_category": None, "census_table": None},
        "09": {"bls_series": None, "mit_category": None, "census_table": None},
        "10": {"bls_series": None, "mit_category": None, "census_table": None},
    }
    result = []
    for code, domain in DOMAINS.items():
        m = mappings.get(code, {})
        result.append({
            "code": code,
            "name": domain.name,
            "description": domain.description,
            "data_sources": {
                "bls_cpi_series": m.get("bls_series"),
                "mit_living_wage": m.get("mit_category"),
                "census_acs": m.get("census_table"),
            },
        })
    return result


# === POLICY ASSESSMENT ===

@mcp.tool
def assess_policy(name: str, description: str, jurisdiction: str = "") -> dict:
    """Start a new policy assessment. Returns the assessment ID.

    Args:
        name: Short policy name (e.g., "Raise minimum wage to $20/hr")
        description: Full description of the policy
        jurisdiction: Where it applies (e.g., "Ohio", "Los Angeles County")
    """
    assessment = PolicyAssessment(
        policy_name=name,
        policy_description=description,
        jurisdiction=jurisdiction,
    )
    _assessments[name] = assessment
    return {
        "status": "Assessment started",
        "policy": name,
        "next_steps": [
            "Use add_end_impact() to assess which hedonic domains are affected",
            "Use add_means_impact() to assess which costs are modified",
            "Use add_distribution() to assess who gains and who bears costs",
            "Use get_policy_assessment() to see the full analysis",
        ],
    }


@mcp.tool
def add_end_impact(policy_name: str, domain_code: str, direction: str,
                   magnitude: str, affected_population: str = "",
                   affected_count: str = "", notes: str = "") -> dict:
    """Add a hedonic END impact to a policy assessment.

    Args:
        policy_name: Name of the policy being assessed
        domain_code: Hedonic domain affected (01-10)
        direction: improved | worsened | unchanged | uncertain
        magnitude: marginal | moderate | significant | transformative
        affected_population: Who is affected (e.g., "low-wage workers")
        affected_count: How many (e.g., "340,000 workers")
    """
    if policy_name not in _assessments:
        return {"error": f"No assessment found for '{policy_name}'. Run assess_policy first."}
    _assessments[policy_name].add_end_impact(
        domain_code, direction, magnitude,
        affected_population, affected_count, notes,
    )
    return {"status": "End impact added", "impacts_so_far": len(_assessments[policy_name].impacts)}


@mcp.tool
def add_means_impact(policy_name: str, cost_category: str, direction: str,
                     magnitude: str, affected_population: str = "",
                     affected_count: str = "", notes: str = "") -> dict:
    """Add a MEANS/cost impact to a policy assessment.

    Args:
        policy_name: Name of the policy being assessed
        cost_category: Cost category affected (T, F, A, P, S, E, R, K, X)
        direction: improved (decreased) | worsened (increased) | unchanged | uncertain
        magnitude: marginal | moderate | significant | transformative
        affected_population: Who bears/benefits from this cost change
    """
    if policy_name not in _assessments:
        return {"error": f"No assessment found for '{policy_name}'. Run assess_policy first."}
    _assessments[policy_name].add_means_impact(
        cost_category, direction, magnitude,
        affected_population, affected_count, notes,
    )
    return {"status": "Means impact added", "impacts_so_far": len(_assessments[policy_name].impacts)}


@mcp.tool
def add_distribution(policy_name: str, group: str, effect: str,
                     domains: list[str] = None, costs: list[str] = None,
                     notes: str = "") -> dict:
    """Add a distributional effect — who gains hedonic value, who bears costs.

    Args:
        policy_name: Name of the policy
        group: Who (e.g., "low-wage workers", "employers", "taxpayers")
        effect: "gains hedonic value" | "bears increased cost" | "mixed"
        domains: Which hedonic domains affected for this group
        costs: Which cost categories affected for this group
    """
    if policy_name not in _assessments:
        return {"error": f"No assessment found for '{policy_name}'. Run assess_policy first."}
    _assessments[policy_name].add_distributional_effect(
        group, effect, domains, costs, notes,
    )
    return {"status": "Distribution added",
            "groups_so_far": len(_assessments[policy_name].distributional)}


@mcp.tool
def save_assessment(policy_name: str) -> dict:
    """Save a policy assessment to shared hedonics storage (~/.hedonics/).
    Other tools can then reference and grade it."""
    if policy_name not in _assessments:
        return {"error": f"No assessment found for '{policy_name}'."}
    data = _assessments[policy_name].to_dict()
    saved_path = save_policy_assessment(policy_name, data)
    return {"saved_to": str(saved_path), "policy": policy_name}


@mcp.tool
def load_saved_assessment(policy_name: str) -> dict:
    """Load a previously saved policy assessment from shared storage."""
    result = load_policy_assessment(policy_name)
    if result:
        return result
    return {"error": f"No saved assessment for '{policy_name}'."}


@mcp.tool
def get_policy_assessment(policy_name: str) -> dict:
    """Get the full hedonic assessment of a policy."""
    if policy_name not in _assessments:
        return {"error": f"No assessment found for '{policy_name}'."}
    return _assessments[policy_name].to_dict()


@mcp.tool
def list_policy_assessments() -> list[str]:
    """List all policy assessments in this session."""
    return list(_assessments.keys())


if __name__ == "__main__":
    mcp.run()
