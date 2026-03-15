"""
High Noon CLI — standalone software purpose assessment.

Usage:
    highnoon scan [path]        Scan a project for signals
    highnoon assess [path]      Start an assessment
"""

import argparse
import json
import sys

from highnoon.assess import read_project_signals, SoftwareAssessment


def cmd_scan(args):
    path = args.path or "."
    signals = read_project_signals(path)
    print(f"\n  Project: {signals.get('name', 'unknown')}")
    print(f"  Path: {signals.get('path', path)}")
    print(f"  README: {'yes' if 'readme' in signals else 'no'}")
    print(f"  pyproject.toml: {'yes' if 'pyproject' in signals else 'no'}")
    print(f"  package.json: {'yes' if 'package_json' in signals else 'no'}")
    if "readme" in signals:
        preview = signals["readme"][:300].replace("\n", "\n    ")
        print(f"\n  README preview:\n    {preview}")
    print()


def cmd_assess(args):
    path = args.path or "."
    signals = read_project_signals(path)
    print(f"\n  High Noon Assessment: {signals.get('name', 'unknown')}")
    print(f"  Path: {signals.get('path', path)}")
    print(f"\n  For full LLM-assisted assessment, use the MCP server:")
    print(f"    python -m highnoon.mcp")
    print(f"\n  Or pipe to an LLM:")
    print(f"    highnoon scan {path} | claude 'classify this project by human purpose'")
    print()


def cmd_json(args):
    path = args.path or "."
    signals = read_project_signals(path)
    print(json.dumps(signals, indent=2, default=str))


def main():
    parser = argparse.ArgumentParser(
        prog="highnoon",
        description="High Noon — Software purpose assessment",
    )
    sub = parser.add_subparsers(dest="command")

    p_scan = sub.add_parser("scan", help="Scan a project for signals")
    p_scan.add_argument("path", nargs="?", default=".", help="Project directory")

    p_assess = sub.add_parser("assess", help="Start a purpose assessment")
    p_assess.add_argument("path", nargs="?", default=".", help="Project directory")

    p_json = sub.add_parser("json", help="Output project signals as JSON")
    p_json.add_argument("path", nargs="?", default=".", help="Project directory")

    sub.add_parser("save", help="Show saved software assessments")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands = {
        "scan": cmd_scan,
        "assess": cmd_assess,
        "json": cmd_json,
        "save": cmd_save,
    }
    commands[args.command](args)


def cmd_save(args):
    from hedonics.storage import list_software_assessments, list_grades
    software = list_software_assessments()
    grades = list_grades("software")
    print(f"\n  High Noon — Saved Software Assessments")
    print(f"  Assessed: {len(software)} projects")
    for s in software:
        print(f"    - {s['project']} ({s['assessed_at'][:10]})")
    print(f"\n  Graded: {len(grades)} projects")
    for g in grades:
        tags = g.get("seo_tags", [])
        htc = [t for t in tags if t.startswith("serves-")]
        hqc = [t for t in tags if t.startswith("reduces-") or t.startswith("increases-")]
        print(f"    {g['overall_grade']:<3} {g['item_name']}")
        if htc:
            print(f"        ends:  {' '.join(htc)}")
        if hqc:
            print(f"        costs: {' '.join(hqc)}")
        if tags:
            print(f"        tags:  {' | '.join(tags)}")
    print(f"\n  Storage: ~/.hedonics/software/")
    print()


if __name__ == "__main__":
    main()
