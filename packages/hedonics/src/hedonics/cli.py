"""
Hedonics CLI — standalone command-line interface.

Usage:
    hedonics domains          List all 10 hedonic domains
    hedonics domain 07        Get details for a specific domain
    hedonics classify "..."   Classify a purpose description
    hedonics costs            List cost categories
"""

import argparse
import json
import sys

from hedonics.taxonomy import DOMAINS, get_domain, list_domains
from hedonics.htc import QUALITY_MODIFIERS
from hedonics.hqc import COST_CATEGORIES


def cmd_domains(args):
    for d in list_domains():
        print(f"  {d.code}  {d.name:<14}  {d.description}")


def cmd_domain(args):
    d = get_domain(args.code)
    print(f"\n  {d.code}  {d.name}")
    print(f"  {d.description}\n")
    print(f"  Examples: {', '.join(d.examples)}")
    if d.atus_mapping:
        print(f"  ATUS: {', '.join(d.atus_mapping)}")
    if d.mit_mapping:
        print(f"  MIT Living Wage: {d.mit_mapping}")
    print()


def cmd_classify(args):
    description = " ".join(args.description)
    description_lower = description.lower()
    keywords = {
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
    found = False
    for code, words in keywords.items():
        matched = [w for w in words if w in description_lower]
        if matched:
            d = DOMAINS[code]
            print(f"  HTC {code}  {d.name:<14}  (matched: {', '.join(matched)})")
            found = True
    if not found:
        print("  No matches found. Try describing the human purpose more specifically.")


def cmd_costs(args):
    for code, name in COST_CATEGORIES.items():
        print(f"  {code}  {name}")


def cmd_json(args):
    """Output full taxonomy as JSON for piping."""
    data = {
        "domains": [
            {"code": d.code, "name": d.name, "description": d.description, "examples": d.examples}
            for d in list_domains()
        ],
        "quality_modifiers": QUALITY_MODIFIERS,
        "cost_categories": COST_CATEGORIES,
    }
    print(json.dumps(data, indent=2))


def main():
    parser = argparse.ArgumentParser(
        prog="hedonics",
        description="Human Hedonics Teleology Classification System",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("domains", help="List all 10 hedonic domains")

    p_domain = sub.add_parser("domain", help="Get details for a domain")
    p_domain.add_argument("code", help="Domain code (01-10) or name (e.g., CONNECTION)")

    p_classify = sub.add_parser("classify", help="Classify a purpose description")
    p_classify.add_argument("description", nargs="+", help="Natural language description")

    sub.add_parser("costs", help="List cost categories")
    sub.add_parser("json", help="Output full taxonomy as JSON")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands = {
        "domains": cmd_domains,
        "domain": cmd_domain,
        "classify": cmd_classify,
        "costs": cmd_costs,
        "json": cmd_json,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
