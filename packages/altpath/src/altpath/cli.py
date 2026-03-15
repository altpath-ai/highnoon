"""
AltPath CLI — standalone personal hedonic assessment.

Usage:
    altpath domains         List the 10 hedonic domains
    altpath assess          Interactive self-assessment
    altpath score 07 4      Score a domain directly
"""

import argparse
import json
import sys

from altpath.assessment import Assessment
from hedonics.taxonomy import DOMAINS, list_domains


def cmd_domains(args):
    print("\n  The 10 Hedonic Life Domains:\n")
    for d in list_domains():
        print(f"  {d.code}  {d.name:<14}  {d.description}")
    print()


def cmd_assess(args):
    """Interactive assessment — score each domain."""
    print("\n  AltPath Hedonic Life Assessment")
    print("  Score each domain 1-10 (or 's' to skip)\n")
    assessment = Assessment()
    for d in list_domains():
        while True:
            raw = input(f"  {d.code} {d.name:<14} (1-10, s=skip): ").strip()
            if raw.lower() == "s":
                break
            try:
                val = float(raw)
                if 1 <= val <= 10:
                    notes = input(f"     Notes (optional): ").strip()
                    assessment.score_domain(d.code, val, notes)
                    break
                else:
                    print("     Please enter a number 1-10")
            except ValueError:
                print("     Please enter a number 1-10")

    print("\n  Results:")
    print(f"  Hedonic Index: {assessment.hedonic_index():.1f}/10\n")

    if assessment.gaps():
        print("  Gaps (need attention):")
        for s in assessment.gaps():
            print(f"    {s.domain_code} {s.domain_name:<14} {s.score}/10  [{s.level}]")
        print()

    if assessment.strengths():
        print("  Strengths (thriving):")
        for s in assessment.strengths():
            print(f"    {s.domain_code} {s.domain_name:<14} {s.score}/10  [{s.level}]")
        print()


def cmd_score(args):
    assessment = Assessment()
    assessment.score_domain(args.code, float(args.value), args.notes or "")
    s = assessment.scores[args.code]
    print(f"\n  {s.domain_code} {s.domain_name}: {s.score}/10 [{s.level}]")
    if s.notes:
        print(f"  Notes: {s.notes}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="altpath",
        description="AltPath — Personal hedonic life assessment",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("domains", help="List the 10 hedonic domains")
    sub.add_parser("assess", help="Interactive self-assessment")

    p_score = sub.add_parser("score", help="Score a single domain")
    p_score.add_argument("code", help="Domain code (01-10)")
    p_score.add_argument("value", help="Score (1-10)")
    p_score.add_argument("--notes", help="Optional notes", default="")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands = {
        "domains": cmd_domains,
        "assess": cmd_assess,
        "score": cmd_score,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
