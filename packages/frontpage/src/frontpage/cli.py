"""
Front Page CLI — hedonically-optimized content discovery.

Usage:
    frontpage suggest 07        Suggest searches for a gap domain
    frontpage sources           List available content sources
    frontpage types             List content types
"""

import argparse
import json
import sys

from frontpage.sources import get_search_terms, get_key_datasets, SOURCE_REGISTRY
from frontpage.feed import CONTENT_TYPES
from hedonics.taxonomy import DOMAINS
from hedonics.hqc import COST_CATEGORIES


def cmd_suggest(args):
    code = args.domain_code
    if code not in DOMAINS:
        print(f"  Unknown domain: {code}. Valid: 01-10")
        return
    domain = DOMAINS[code]
    terms = get_search_terms(code)
    datasets = get_key_datasets(code)

    print(f"\n  Front Page — Suggested Discovery for {domain.name}\n")
    print(f"  \"{domain.description}\"\n")

    if terms:
        print(f"  Research search terms:")
        for t in terms:
            print(f"    - {t}")
        print()

    if datasets:
        print(f"  Key open datasets:")
        for d in datasets:
            print(f"    - {d}")
        print()

    if not terms and not datasets:
        print(f"  No specific suggestions mapped yet for {domain.name}.")
        print(f"  Use the MCP server for LLM-assisted discovery.")
    print()


def cmd_sources(args):
    print("\n  Front Page — Content Sources:\n")
    for source_type, info in SOURCE_REGISTRY.items():
        print(f"  {source_type}")
        print(f"    {info['description']}")
        connectors = info.get("connectors", [])
        if connectors:
            print(f"    Connectors: {', '.join(connectors)}")
        print()


def cmd_types(args):
    print("\n  Front Page — Content Types:\n")
    for t in CONTENT_TYPES:
        desc = SOURCE_REGISTRY.get(t, {}).get("description", "")
        print(f"  {t:<12} {desc}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="frontpage",
        description="Front Page — The front page of your hedonic life",
    )
    sub = parser.add_subparsers(dest="command")

    p_suggest = sub.add_parser("suggest", help="Suggest searches for a gap domain")
    p_suggest.add_argument("domain_code", help="Domain code (01-10)")

    sub.add_parser("sources", help="List available content sources")
    sub.add_parser("types", help="List content types")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands = {
        "suggest": cmd_suggest,
        "sources": cmd_sources,
        "types": cmd_types,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
