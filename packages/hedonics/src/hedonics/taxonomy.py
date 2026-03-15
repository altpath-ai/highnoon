"""
The 10 hedonic domains — the Dewey decimal of human purposes.

Grounded in:
- BLS American Time Use Survey (ATUS)
- MIT Living Wage Calculator
- BLS CPI hedonic quality adjustment methodology
"""

from dataclasses import dataclass, field


@dataclass
class Domain:
    """A hedonic life domain — an area of intrinsic human value."""
    code: str
    name: str
    description: str
    examples: list[str] = field(default_factory=list)
    atus_mapping: list[str] = field(default_factory=list)
    mit_mapping: str = ""


DOMAINS = {
    "01": Domain(
        code="01",
        name="NOURISHMENT",
        description="Eating, drinking, savoring — the hedonic experience of sustenance",
        examples=["sharing a meal", "tasting something new", "cooking for pleasure"],
        atus_mapping=["11 - Eating and Drinking", "02.02 - Food Preparation"],
        mit_mapping="Food",
    ),
    "02": Domain(
        code="02",
        name="SHELTER",
        description="Comfort, rest, safety, home — the hedonic experience of dwelling",
        examples=["resting in a comfortable space", "feeling safe", "sleeping well"],
        atus_mapping=["01 - Personal Care", "02.01 - Housework"],
        mit_mapping="Housing",
    ),
    "03": Domain(
        code="03",
        name="HEALTH",
        description="Vitality, wellness, bodily integrity — the hedonic experience of being well",
        examples=["feeling energetic", "recovery from illness", "physical vitality"],
        atus_mapping=["01.03 - Health-related self-care"],
        mit_mapping="Healthcare",
    ),
    "04": Domain(
        code="04",
        name="CARE",
        description="Nurturing, bonding, love — the hedonic experience of caring and being cared for",
        examples=["holding a child", "being comforted", "caring for a loved one"],
        atus_mapping=["03 - Caring for Household Members", "04 - Caring for Non-HH Members"],
        mit_mapping="Childcare",
    ),
    "05": Domain(
        code="05",
        name="MOBILITY",
        description="Movement as experience — freedom, exploration, travel for its own sake",
        examples=["road trip", "exploring a new city", "a walk in nature"],
        atus_mapping=["17 - Traveling (non-instrumental)"],
        mit_mapping="Transportation",
    ),
    "06": Domain(
        code="06",
        name="GROWTH",
        description="Learning, mastery, curiosity — the hedonic experience of becoming more",
        examples=["understanding something deeply", "acquiring a new skill", "reading"],
        atus_mapping=["06 - Education"],
        mit_mapping="Civic Engagement (education component)",
    ),
    "07": Domain(
        code="07",
        name="CONNECTION",
        description="Belonging, intimacy, community — the hedonic experience of being with others",
        examples=["deep conversation", "feeling understood", "community gathering"],
        atus_mapping=["12 - Socializing", "16 - Communication"],
        mit_mapping="Internet & Communication",
    ),
    "08": Domain(
        code="08",
        name="RECREATION",
        description="Play, leisure, entertainment, beauty — the hedonic experience of enjoyment",
        examples=["playing a game", "watching a sunset", "listening to music"],
        atus_mapping=["12 - Relaxing/Leisure", "13 - Sports/Exercise/Recreation"],
        mit_mapping="Civic Engagement (recreation component)",
    ),
    "09": Domain(
        code="09",
        name="EXPRESSION",
        description="Creating, making, self-actualization — the hedonic experience of bringing something new into being",
        examples=["writing", "painting", "building something", "performing"],
        atus_mapping=["12.04 - Arts and Entertainment"],
        mit_mapping="",
    ),
    "10": Domain(
        code="10",
        name="MEANING",
        description="Purpose, identity, legacy, transcendence — the hedonic experience of mattering",
        examples=["spiritual practice", "contributing to something larger", "reflection"],
        atus_mapping=["14 - Religious/Spiritual", "15 - Volunteer Activities"],
        mit_mapping="",
    ),
}


def get_domain(code: str) -> Domain:
    """Get a domain by its code (e.g., '07' for CONNECTION)."""
    if code in DOMAINS:
        return DOMAINS[code]
    # Try by name
    for d in DOMAINS.values():
        if d.name.upper() == code.upper():
            return d
    raise KeyError(f"Unknown domain: {code}. Valid codes: {list(DOMAINS.keys())}")


def list_domains() -> list[Domain]:
    """List all 10 hedonic domains."""
    return list(DOMAINS.values())
