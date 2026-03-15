"""
Hedonics CLI — standalone command-line interface.

Usage:
    hedonics domains          List all 10 hedonic domains (ENDS)
    hedonics domain 07        Get details for a specific domain
    hedonics classify "..."   Classify a purpose description
    hedonics costs            List all cost categories (MEANS)
    hedonics cost T           Get subcategories for a cost
    hedonics blockers 07      Show typical costs that block a domain
"""

import argparse
import json
import sys

from hedonics.taxonomy import DOMAINS, get_domain, list_domains
from hedonics.htc import QUALITY_MODIFIERS
from hedonics.hqc import COST_CATEGORIES, COST_SUBCATEGORIES, list_all_costs


# Which costs typically block access to which domains
DOMAIN_BLOCKERS = {
    "01": [("F.1", "Can't afford quality food"), ("T.2", "No time to cook"), ("K.3", "Don't know nutrition basics")],
    "02": [("F.1", "Can't afford adequate housing"), ("T.6", "No time for home maintenance"), ("R.1", "Regulatory barriers to housing")],
    "03": [("F.1", "Can't afford healthcare"), ("T.1", "Work leaves no time for exercise"), ("A.1", "Too stressed to focus on wellness")],
    "04": [("T.1", "Work consumes all time for caregiving"), ("A.1", "Emotional exhaustion from cognitive load"), ("F.1", "Can't afford childcare support")],
    "05": [("F.1", "Can't afford to travel"), ("T.1", "No time off from work"), ("P.1", "Physical limitations on movement")],
    "06": [("T.1", "Work leaves no time to learn"), ("F.1", "Can't afford education"), ("A.1", "Cognitive load prevents study"), ("T.7", "Learning curve too steep")],
    "07": [("T.1", "Work consumes all social time"), ("A.1", "Too mentally exhausted"), ("X.1", "Status anxiety prevents socializing"), ("P.4", "Sensory overload in social settings")],
    "08": [("T.1", "No leisure time"), ("F.1", "Can't afford recreation"), ("A.1", "Too drained for play"), ("P.2", "Physical pain prevents activity")],
    "09": [("T.1", "No time to create"), ("A.1", "No creative bandwidth"), ("K.1", "Don't know where to start"), ("X.3", "Fear of judgment")],
    "10": [("T.1", "Survival mode — no time for reflection"), ("A.2", "Uncertainty blocks meaning-making"), ("S.2", "No community for shared meaning")],
}


def cmd_domains(args):
    print("\n  ENDS — The 10 Hedonic Domains (what humans value intrinsically):\n")
    for d in list_domains():
        print(f"  {d.code}  {d.name:<14}  {d.description}")
    print()


def cmd_domain(args):
    d = get_domain(args.code)
    print(f"\n  {d.code}  {d.name}")
    print(f"  {d.description}\n")
    print(f"  Examples: {', '.join(d.examples)}")
    if d.atus_mapping:
        print(f"  ATUS: {', '.join(d.atus_mapping)}")
    if d.mit_mapping:
        print(f"  MIT Living Wage: {d.mit_mapping}")

    blockers = DOMAIN_BLOCKERS.get(d.code, [])
    if blockers:
        print(f"\n  Common cost blockers (MEANS that lock this END):")
        for cost_code, desc in blockers:
            print(f"    {cost_code:<6} {desc}")
    print()


def cmd_classify(args):
    description = " ".join(args.description)
    description_lower = description.lower()

    # Ends keywords
    end_keywords = {
        "01": ["food", "eat", "meal", "cook", "nourish", "nutrition", "diet", "drink"],
        "02": ["home", "house", "shelter", "sleep", "rest", "comfort", "safe", "housing"],
        "03": ["health", "medical", "wellness", "exercise", "fitness", "vitality", "therapy"],
        "04": ["care", "child", "parent", "nurtur", "elder", "family", "love", "bond"],
        "05": ["travel", "transport", "move", "explor", "trip", "journey", "drive"],
        "06": ["learn", "educat", "skill", "grow", "study", "knowledge", "master", "course"],
        "07": ["connect", "social", "communit", "friend", "relationship", "belong", "chat", "message"],
        "08": ["play", "game", "fun", "entertain", "recreation", "leisure", "music", "art", "sport"],
        "09": ["create", "make", "build", "write", "design", "express", "craft", "paint"],
        "10": ["meaning", "purpose", "spirit", "identity", "legacy", "volunteer", "faith", "reflect"],
    }

    # Means keywords — what costs does this description touch?
    means_keywords = {
        "T": ["time", "hour", "minutes", "schedule", "wait", "fast", "slow", "quick", "efficient", "automate"],
        "F": ["cost", "price", "money", "afford", "cheap", "expensive", "budget", "save", "free", "pay"],
        "A": ["attention", "focus", "cognitive", "distract", "overwhelm", "simple", "easy", "complex", "confus"],
        "P": ["effort", "physical", "pain", "comfort", "exert", "exhaust", "energy", "fatigue"],
        "S": ["privacy", "relationship", "reputation", "trust", "obligation", "social cost"],
        "E": ["carbon", "emission", "waste", "environment", "sustain", "green", "eco"],
        "R": ["compliance", "regulation", "legal", "license", "audit", "liability"],
        "K": ["uncertain", "ambiguous", "opaque", "transparent", "understand", "clarity", "risk"],
        "X": ["status", "credential", "prestige", "signal", "brand", "reputation"],
    }

    found_ends = False
    found_means = False

    # Check ends
    for code, words in end_keywords.items():
        matched = [w for w in words if w in description_lower]
        if matched:
            if not found_ends:
                print("\n  ENDS served (hedonic domains):")
                found_ends = True
            d = DOMAINS[code]
            print(f"    HTC {code}  {d.name:<14}  (matched: {', '.join(matched)})")

    # Check means
    for code, words in means_keywords.items():
        matched = [w for w in words if w in description_lower]
        if matched:
            if not found_means:
                print("\n  MEANS modified (cost categories):")
                found_means = True
            print(f"    HQC {code}   {COST_CATEGORIES[code]:<14}  (matched: {', '.join(matched)})")

    if not found_ends and not found_means:
        print("  No matches found. Try describing both the human purpose AND the costs involved.")
    print()


def cmd_costs(args):
    print("\n  MEANS — The 9 Fungible Cost Categories:\n")
    for cost in list_all_costs():
        print(f"  {cost['code']}  {cost['name']}")
        for sub in cost["subcategories"]:
            print(f"       {sub['code']}  {sub['description']}")
        print()


def cmd_cost(args):
    cat = args.category.upper()
    if cat not in COST_CATEGORIES:
        print(f"  Unknown category: {cat}. Valid: {', '.join(COST_CATEGORIES.keys())}")
        return
    subs = COST_SUBCATEGORIES.get(cat, {})
    print(f"\n  {cat}  {COST_CATEGORIES[cat]}\n")
    for sub_code, desc in subs.items():
        print(f"    {cat}.{sub_code}  {desc}")
    print()


def cmd_blockers(args):
    code = args.domain_code
    if code not in DOMAINS:
        print(f"  Unknown domain: {code}. Valid: 01-10")
        return
    d = DOMAINS[code]
    blockers = DOMAIN_BLOCKERS.get(code, [])
    print(f"\n  Cost blockers for {d.code} {d.name}:")
    print(f"  \"{d.description}\"\n")
    if blockers:
        for cost_code, desc in blockers:
            print(f"    {cost_code:<6}  {desc}")
        print(f"\n  Tools that DECREASE these costs unlock access to {d.name}.")
    else:
        print("    No common blockers mapped yet.")
    print()


def cmd_json(args):
    """Output full taxonomy as JSON for piping."""
    data = {
        "ends": {
            "label": "Hedonic Domains (intrinsic value)",
            "domains": [
                {"code": d.code, "name": d.name, "description": d.description, "examples": d.examples}
                for d in list_domains()
            ],
        },
        "means": {
            "label": "Fungible Cost Categories (instrumental)",
            "categories": list_all_costs(),
        },
        "blockers": {
            code: [{"cost": c, "description": d} for c, d in blockers]
            for code, blockers in DOMAIN_BLOCKERS.items()
        },
        "quality_modifiers": QUALITY_MODIFIERS,
    }
    print(json.dumps(data, indent=2))


def cmd_save(args):
    """Show all saved data across the hedonics ecosystem."""
    from hedonics.storage import load_profile, list_software_assessments, list_policy_assessments, list_grades, grade_summary

    profile = load_profile()
    software = list_software_assessments()
    policies = list_policy_assessments()
    summary = grade_summary()

    print("\n  Hedonics Ecosystem — Saved Data (~/.hedonics/)")
    print("  ================================================\n")

    if profile:
        hi = sum(e["score"] for e in profile.get("ends", [])) / max(len(profile.get("ends", [])), 1)
        print(f"  Profile:     saved ({profile.get('saved_at', '?')[:19]}), Hedonic Index: {hi:.1f}/10")
    else:
        print("  Profile:     not yet assessed (run: altpath assess)")

    print(f"  Software:    {len(software)} assessed")
    for s in software[:3]:
        print(f"               - {s['project']}")

    print(f"  Policies:    {len(policies)} assessed")
    for p in policies[:3]:
        print(f"               - {p['policy']}")

    print(f"  Grades:      {summary['total_graded']} total")
    for t, info in summary.get("by_type", {}).items():
        grades_str = ", ".join(f"{g}:{c}" for g, c in info["grades"].items())
        print(f"               {t}: {info['count']} ({grades_str})")

    print(f"\n  Storage: ~/.hedonics/")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="hedonics",
        description="Human Hedonics Teleology Classification System — ENDS and MEANS",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("domains", help="List all 10 hedonic domains (ENDS)")

    p_domain = sub.add_parser("domain", help="Get details for a domain + its cost blockers")
    p_domain.add_argument("code", help="Domain code (01-10) or name (e.g., CONNECTION)")

    p_classify = sub.add_parser("classify", help="Classify by both ENDS served and MEANS modified")
    p_classify.add_argument("description", nargs="+", help="Natural language description")

    sub.add_parser("costs", help="List all cost categories with subcategories (MEANS)")

    p_cost = sub.add_parser("cost", help="Get subcategories for a specific cost")
    p_cost.add_argument("category", help="Cost category (T, F, A, P, S, E, R, K, X)")

    p_blockers = sub.add_parser("blockers", help="Show costs that block access to a domain")
    p_blockers.add_argument("domain_code", help="Domain code (01-10)")

    sub.add_parser("json", help="Output full taxonomy as JSON")
    sub.add_parser("save", help="Show all saved data across the ecosystem")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands = {
        "domains": cmd_domains,
        "domain": cmd_domain,
        "classify": cmd_classify,
        "costs": cmd_costs,
        "cost": cmd_cost,
        "blockers": cmd_blockers,
        "json": cmd_json,
        "save": cmd_save,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
