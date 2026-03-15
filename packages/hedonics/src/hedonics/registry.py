"""
Hedonic Registry — searchable index of graded items across the ecosystem.

The registry indexes all grades (software, policy, content) and makes them
searchable by:
- Hedonic domain (HTC): "find everything that serves HEALTH"
- Cost modification (HQC): "find everything that reduces ATTENTION"
- Grade: "find all A-rated tools"
- SEO tags: full-text search across all tags
- Combined queries: "serves-health AND reduces-attention-cost AND grade-A"

Storage: ~/.hedonics/registry/index.json
Rebuilt from grades on demand. The grades are the source of truth.
"""

import json
from pathlib import Path
from datetime import datetime
from hedonics.storage import list_grades, HEDONICS_DIR
from hedonics.taxonomy import DOMAINS
from hedonics.hqc import COST_CATEGORIES


REGISTRY_DIR = HEDONICS_DIR / "registry"
INDEX_FILE = REGISTRY_DIR / "index.json"


def rebuild_index() -> dict:
    """Rebuild the registry index from all stored grades."""
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

    all_grades = list_grades()

    # Build searchable indices
    by_domain = {}      # domain_code → [items]
    by_cost = {}        # cost_code → [items]
    by_grade = {}       # letter → [items]
    by_type = {}        # item_type → [items]
    by_tag = {}         # tag → [items]
    items = []

    for g in all_grades:
        entry = {
            "name": g.get("item_name", ""),
            "type": g.get("item_type", ""),
            "grade": g.get("overall_grade", ""),
            "purpose_score": g.get("purpose_score", 0),
            "cost_efficiency": g.get("cost_efficiency", 0),
            "relevance_score": g.get("relevance_score", 0),
            "domains": g.get("domains_served", []),
            "costs": g.get("costs_modified", []),
            "cost_effects": g.get("cost_effects", {}),
            "tags": g.get("seo_tags", []),
            "notes": g.get("notes", ""),
            "graded_at": g.get("graded_at", ""),
        }
        items.append(entry)

        # Index by domain
        for d in entry["domains"]:
            by_domain.setdefault(d, []).append(entry["name"])

        # Index by cost
        for c in entry["costs"]:
            by_cost.setdefault(c, []).append(entry["name"])

        # Index by grade
        by_grade.setdefault(entry["grade"], []).append(entry["name"])

        # Index by type
        by_type.setdefault(entry["type"], []).append(entry["name"])

        # Index by tag
        for tag in entry["tags"]:
            by_tag.setdefault(tag, []).append(entry["name"])

    index = {
        "rebuilt_at": datetime.now().isoformat(),
        "total_items": len(items),
        "items": items,
        "by_domain": by_domain,
        "by_cost": by_cost,
        "by_grade": by_grade,
        "by_type": by_type,
        "by_tag": by_tag,
    }

    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)

    return index


def load_index() -> dict:
    """Load the registry index. Rebuilds if stale or missing."""
    if INDEX_FILE.exists():
        with open(INDEX_FILE) as f:
            return json.load(f)
    return rebuild_index()


def search(query: str = "", domains: list[str] = None, costs: list[str] = None,
           grade: str = "", item_type: str = "", cost_direction: str = "",
           min_purpose: float = 0, min_relevance: float = 0) -> list[dict]:
    """Search the registry with flexible filters.

    Args:
        query: Free-text search across tags and names (e.g., "serves-health reduces-attention")
        domains: Filter by HTC domains served (e.g., ["03", "04"])
        costs: Filter by HQC costs modified (e.g., ["A", "T"])
        grade: Filter by minimum grade (e.g., "B" matches B, B+, A, A+)
        item_type: Filter by type ("software", "policy", "content")
        cost_direction: Filter by cost direction ("decreased" or "increased")
        min_purpose: Minimum purpose score (0-10)
        min_relevance: Minimum relevance score (0-10)

    Returns:
        Matching items sorted by relevance score (highest first)
    """
    index = load_index()
    results = []

    grade_order = {"A+": 9, "A": 8, "B+": 7, "B": 6, "C+": 5, "C": 4, "D": 3, "F": 1}
    min_grade_val = grade_order.get(grade, 0) if grade else 0

    for item in index.get("items", []):
        # Domain filter
        if domains and not any(d in item["domains"] for d in domains):
            continue

        # Cost filter
        if costs and not any(c in item["costs"] for c in costs):
            continue

        # Grade filter
        item_grade_val = grade_order.get(item["grade"], 0)
        if min_grade_val and item_grade_val < min_grade_val:
            continue

        # Type filter
        if item_type and item["type"] != item_type:
            continue

        # Cost direction filter
        if cost_direction:
            effects = item.get("cost_effects", {})
            has_direction = any(
                e.get("direction") == cost_direction
                for e in effects.values()
            )
            if not has_direction:
                continue

        # Score filters
        if min_purpose and item["purpose_score"] < min_purpose:
            continue
        if min_relevance and item["relevance_score"] < min_relevance:
            continue

        # Free-text query across tags + name + notes
        if query:
            query_terms = query.lower().split()
            searchable = " ".join(item["tags"] + [item["name"], item["notes"]]).lower()
            if not all(term in searchable for term in query_terms):
                continue

        results.append(item)

    # Sort by relevance, then purpose score
    results.sort(key=lambda r: (r["relevance_score"], r["purpose_score"]), reverse=True)
    return results


def search_by_need(domain_code: str) -> list[dict]:
    """Shortcut: find everything that serves a specific hedonic need."""
    return search(domains=[domain_code], cost_direction="decreased")


def search_cost_reducers(cost_code: str) -> list[dict]:
    """Shortcut: find everything that reduces a specific cost."""
    return search(costs=[cost_code], cost_direction="decreased")


def registry_stats() -> dict:
    """Summary statistics for the registry."""
    index = load_index()
    return {
        "total_items": index.get("total_items", 0),
        "rebuilt_at": index.get("rebuilt_at", ""),
        "by_type": {t: len(items) for t, items in index.get("by_type", {}).items()},
        "by_grade": {g: len(items) for g, items in index.get("by_grade", {}).items()},
        "domains_covered": {
            d: {"name": DOMAINS[d].name, "count": len(items)}
            for d, items in index.get("by_domain", {}).items()
            if d in DOMAINS
        },
        "costs_covered": {
            c: {"name": COST_CATEGORIES.get(c, c), "count": len(items)}
            for c, items in index.get("by_cost", {}).items()
        },
    }
