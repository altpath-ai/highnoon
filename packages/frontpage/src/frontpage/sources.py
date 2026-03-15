"""
Content source connectors.

Fetches and tags content from various sources:
- News APIs (RSS, web search)
- Research repositories (arXiv, PubMed, SSRN)
- Software registries (PyPI, GitHub, npm)
- Policy databases (congress.gov, regulations.gov)
- Open data catalogs (data.gov, BLS, Census)
"""

from dataclasses import dataclass, field
from frontpage.feed import FeedItem


# Placeholder sources — each will get a real connector
SOURCE_REGISTRY = {
    "news": {
        "description": "News stories relevant to hedonic domains",
        "connectors": ["rss", "web_search"],
        "example_feeds": [
            "BLS Economic News Releases",
            "MIT Living Wage updates",
            "Census data releases",
        ],
    },
    "research": {
        "description": "Academic research on hedonic quality, well-being, public policy",
        "connectors": ["arxiv", "pubmed", "ssrn", "scholar"],
        "search_terms_by_domain": {
            "01": ["food security", "nutrition policy", "food desert"],
            "02": ["housing affordability", "shelter policy", "homelessness"],
            "03": ["healthcare access", "public health", "mental health policy"],
            "04": ["childcare policy", "eldercare", "family leave"],
            "05": ["transportation equity", "transit access", "mobility justice"],
            "06": ["education access", "skill development", "workforce training"],
            "07": ["social isolation", "community building", "digital divide"],
            "08": ["recreation access", "parks policy", "arts funding"],
            "09": ["creative economy", "arts education", "maker spaces"],
            "10": ["civic engagement", "volunteerism", "purpose and well-being"],
        },
    },
    "tools": {
        "description": "Software tools tagged by hedonic purpose (via highnoon)",
        "connectors": ["pypi", "github", "npm"],
    },
    "policy": {
        "description": "Public policies assessed through the hedonic framework",
        "connectors": ["congress_gov", "regulations_gov", "state_legislatures"],
    },
    "datasets": {
        "description": "Open datasets for hedonic measurement",
        "connectors": ["data_gov", "bls", "census", "who"],
        "key_datasets": {
            "01": ["USDA Food Access Research Atlas", "SNAP participation data"],
            "02": ["HUD Fair Market Rents", "Census Housing data"],
            "03": ["CDC health indicators", "CMS Medicare/Medicaid"],
            "05": ["DOT National Transit Database", "Census commuting data"],
            "06": ["NCES education statistics", "BLS training data"],
            "07": ["FCC broadband data", "Census internet access"],
        },
    },
}


def get_search_terms(domain_code: str) -> list[str]:
    """Get research search terms for a hedonic domain."""
    return (SOURCE_REGISTRY.get("research", {})
            .get("search_terms_by_domain", {})
            .get(domain_code, []))


def get_key_datasets(domain_code: str) -> list[str]:
    """Get key open datasets for a hedonic domain."""
    return (SOURCE_REGISTRY.get("datasets", {})
            .get("key_datasets", {})
            .get(domain_code, []))
