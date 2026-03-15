"""
AltPath CLI — personal hedonic life assessment.

Usage:
    altpath                 Run the full assessment (default)
    altpath assess          Full interactive assessment (ends + means + optimization)
    altpath domains         List the 10 hedonic domains
    altpath costs           List the 9 cost categories
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from altpath.assessment import Assessment
from hedonics.taxonomy import DOMAINS, list_domains
from hedonics.hqc import COST_CATEGORIES

from hedonics.storage import save_profile, load_profile

ALTPATH_DIR = Path.home() / ".altpath"
ASSESSMENT_FILE = ALTPATH_DIR / "assessment.json"
HISTORY_DIR = ALTPATH_DIR / "history"


def cmd_domains(args):
    print("\n  The 10 Hedonic Life Domains (ENDS):\n")
    for d in list_domains():
        print(f"  {d.code}  {d.name:<14}  {d.description}")
    print()


def cmd_costs(args):
    print("\n  The 9 Fungible Cost Categories (MEANS):\n")
    for code, name in COST_CATEGORIES.items():
        print(f"  {code}   {name}")
    print()


def _input_score(prompt):
    """Get a score 1-10 or skip."""
    while True:
        raw = input(prompt).strip()
        if raw.lower() == "s" or raw == "":
            return None
        try:
            val = float(raw)
            if 1 <= val <= 10:
                return val
            print("     Please enter 1-10 (or s to skip)")
        except ValueError:
            print("     Please enter 1-10 (or s to skip)")


def cmd_assess(args):
    """Full interactive assessment: ENDS, MEANS, results, optimization."""
    assessment = Assessment()

    # === STEP 1: ENDS ===
    print("\n  AltPath — Personal Hedonic Life Assessment")
    print("  ==========================================")
    print("\n  STEP 1: Score your ENDS (1-10, s=skip)")
    print("  How satisfied are you in each life domain?\n")

    for d in list_domains():
        val = _input_score(f"  {d.code} {d.name:<14} (1-10): ")
        if val is not None:
            notes = input(f"     Notes (optional): ").strip()
            assessment.score_domain(d.code, val, notes)

    if not assessment.domain_scores:
        print("\n  No domains scored. Run again and score at least a few.")
        return

    # Show interim results
    print(f"\n  Hedonic Index: {assessment.hedonic_index():.1f}/10")
    if assessment.gaps():
        print("  Gaps:", ", ".join(f"{s.domain_name} ({s.score})" for s in assessment.gaps()))

    # === STEP 2: MEANS ===
    print("\n  STEP 2: Score your MEANS (1=negligible, 10=crushing)")
    print("  How much burden does each cost impose on your life?\n")

    cost_descriptions = {
        "T": "TIME        How much of your time is consumed by obligations?",
        "F": "FINANCIAL   How much financial pressure do you feel?",
        "A": "ATTENTION   How mentally exhausted are you?",
        "P": "PHYSICAL    How much physical strain or discomfort?",
        "S": "SOCIAL      How much social obligation or friction?",
        "K": "KNOWLEDGE   How much uncertainty or confusion?",
        "X": "STATUS      How much pressure to maintain appearances?",
    }

    for cat, desc in cost_descriptions.items():
        val = _input_score(f"  {desc} (1-10): ")
        if val is not None:
            notes = input(f"     Notes (optional): ").strip()

            # Ask what domains this cost blocks
            blocks = []
            if val >= 6 and assessment.gaps():
                gap_names = [f"{s.domain_code}={s.domain_name}" for s in assessment.gaps()]
                block_input = input(f"     Does this block any gaps? ({', '.join(gap_names)}) codes: ").strip()
                if block_input:
                    blocks = [b.strip() for b in block_input.split(",")]

            assessment.score_cost(cat, val, notes, blocks)

    # === RESULTS ===
    result = assessment.to_dict()

    print("\n  ==========================================")
    print("  RESULTS")
    print("  ==========================================")
    print(f"\n  Hedonic Index:  {result['hedonic_index']}/10  (your life satisfaction)")
    print(f"  Cost Index:     {result['cost_index']}/10  (your resource drain)")
    print(f"  Net Hedonic:    {result['net_hedonic']}     (positive = more value than cost)")

    # ENDS
    print("\n  ENDS (your life domains):")
    for code, s in result["ends"].items():
        bar = "█" * int(s["score"]) + "░" * (10 - int(s["score"]))
        print(f"    {code} {s['domain']:<14} {bar} {s['score']}/10 [{s['level']}]")

    # MEANS
    if result["means"]:
        print("\n  MEANS (your cost burdens):")
        for cat, c in result["means"].items():
            bar = "█" * int(c["burden"]) + "░" * (10 - int(c["burden"]))
            print(f"    {cat}  {c['category']:<14} {bar} {c['burden']}/10 [{c['level']}]")

    # GAPS
    if result["gaps"]:
        print("\n  GAPS (domains needing attention):")
        for g in result["gaps"]:
            print(f"    {g['code']} {g['domain']:<14} {g['score']}/10")

    # BLOCKED ENDS
    if result["blocked_ends"]:
        print("\n  BLOCKED ENDS (what you want + what's stopping you):")
        for b in result["blocked_ends"]:
            end = b["end"]
            cost = b["blocked_by"]
            print(f"    {end['domain']} ({end['score']}/10) blocked by {cost['name']} (burden {cost['burden']}/10)")
            print(f"      -> {b['action']}")

    # OPTIMIZATION
    if result["optimization"] and not isinstance(result["optimization"][0], dict) or \
       (result["optimization"] and "note" not in result["optimization"][0]):
        print("\n  FUNGIBILITY CALCULUS (trade what you HAVE for what you NEED):")
        for i, ex in enumerate(result["optimization"][:5], 1):
            if "exchange" in ex:
                print(f"    {i}. {ex['exchange']}: {ex['description']}")
                print(f"       Efficiency: {ex['efficiency']:.0%} | Priority: {ex['priority']:.2f}")
                if ex.get("unlocks_domains"):
                    from hedonics.taxonomy import DOMAINS as D
                    names = [D[d].name for d in ex["unlocks_domains"] if d in D]
                    if names:
                        print(f"       Unlocks: {', '.join(names)}")

    # === SAVE ===
    ALTPATH_DIR.mkdir(exist_ok=True)
    HISTORY_DIR.mkdir(exist_ok=True)

    # Save current assessment
    with open(ASSESSMENT_FILE, "w") as f:
        json.dump(result, f, indent=2)

    # Save timestamped copy to history
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_file = HISTORY_DIR / f"assessment_{ts}.json"
    with open(history_file, "w") as f:
        json.dump(result, f, indent=2)

    # Also save to shared hedonics storage
    hedonics_path = save_profile(result)

    print(f"\n  Assessment saved to: {ASSESSMENT_FILE}")
    print(f"  History saved to:    {history_file}")
    print(f"  Shared storage:      {hedonics_path}")
    print(f"  (Other tools can now read your profile via ~/.hedonics/)")

    # === RECOMMEND FRONTPAGE ===
    if result["gaps"]:
        gap_names = [g["domain"] for g in result["gaps"]]
        print(f"\n  ==========================================")
        print(f"  NEXT STEP: Use frontpage to find content that serves YOUR gaps.")
        print(f"  Your gaps: {', '.join(gap_names)}")
        print()
        for g in result["gaps"]:
            print(f"    frontpage suggest {g['code']}    # Find research + datasets for {g['domain']}")
        print()
        print("  Or add frontpage as an MCP server to your LLM for personalized discovery:")
        print("    python -m frontpage.mcp")
    else:
        print("\n  No gaps identified. You're doing well across all domains.")

    print(f"\n  For deeper analysis, add AltPath as an MCP server to your LLM:")
    print(f"    python -m altpath.mcp")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="altpath",
        description="AltPath — Personal hedonic life assessment",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("assess", help="Full interactive assessment (ends + means + optimization)")
    sub.add_parser("domains", help="List the 10 hedonic domains")
    sub.add_parser("costs", help="List the 9 cost categories")

    args = parser.parse_args()

    # Default to assess if no command given
    if args.command is None:
        args.command = "assess"

    commands = {
        "assess": cmd_assess,
        "domains": cmd_domains,
        "costs": cmd_costs,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
