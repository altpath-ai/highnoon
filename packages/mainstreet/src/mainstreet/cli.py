"""
Main Street CLI — public policy hedonic assessment.

Usage:
    mainstreet time-budget           Show how Americans spend their day (ATUS)
    mainstreet bls <series>          Fetch real BLS data
    mainstreet domains               Show hedonic domains with data source mappings
"""

import argparse
import json
import sys

from mainstreet.datasources import get_atus_profile, fetch_bls_series, BLS_SERIES
from hedonics.taxonomy import DOMAINS


def cmd_time_budget(args):
    employed = not args.all_persons
    profile = get_atus_profile(employed)
    label = "Employed Persons" if employed else "All Persons"

    print(f"\n  ATUS Time Budget — {label} (hours/day)\n")
    print(f"  {'Activity':<25} {'Hours':>6}  {'Type':<12}  Notes")
    print(f"  {'─' * 80}")

    for activity, data in profile["activities"].items():
        name = activity.replace("_", " ").title()
        hours = data["hours_per_day"]
        atype = data.get("type", "")
        note = data.get("note", "")[:45]
        print(f"  {name:<25} {hours:>5.2f}  {atype:<12}  {note}")

    tb = profile["time_budget"]
    print(f"\n  Time Budget Summary:")
    print(f"    MEANS (costs):      {tb['means_hours']:.1f} hrs ({tb['means_pct']}%)")
    print(f"    ENDS (purposes):    {tb['ends_hours']:.1f} hrs ({tb['ends_pct']}%)")
    print(f"    PROCESSING (sleep): {tb['processing_hours']:.1f} hrs ({tb['processing_pct']}%)")
    print()


def cmd_bls(args):
    series = args.series
    series_id = BLS_SERIES.get(series, series)
    print(f"\n  Fetching BLS series: {series} ({series_id})...")
    result = fetch_bls_series([series_id])
    if "error" in result:
        print(f"  Error: {result['error']}")
        return
    data = result.get(series_id, [])
    if not data:
        print("  No data returned. Check series ID or try later.")
        return
    print(f"  {'Year':<6} {'Period':<8} {'Value':>10}")
    for d in data[:12]:
        print(f"  {d['year']:<6} {d['period']:<8} {d['value']:>10.1f}")
    print()


def cmd_series(args):
    print("\n  Available BLS Series:\n")
    for name, sid in BLS_SERIES.items():
        print(f"  {name:<25} {sid}")
    print()


def cmd_domains(args):
    mappings = {
        "01": ("cpi_food", "Food", "S2201"),
        "02": ("cpi_housing", "Housing", "DP04"),
        "03": ("cpi_medical", "Healthcare", "S2701"),
        "04": (None, "Childcare", None),
        "05": ("cpi_transport", "Transportation", "S0801"),
        "06": ("cpi_education", "Civic Engagement", "S1501"),
        "07": (None, "Internet & Comm", "S2801"),
        "08": ("cpi_recreation", None, None),
        "09": (None, None, None),
        "10": (None, None, None),
    }
    print("\n  Hedonic Domains — Federal Data Source Mappings:\n")
    print(f"  {'Code':<5} {'Domain':<14} {'BLS CPI':<18} {'MIT Living Wage':<18} {'Census ACS'}")
    print(f"  {'─' * 75}")
    for code, domain in DOMAINS.items():
        bls, mit, census = mappings.get(code, (None, None, None))
        print(f"  {code:<5} {domain.name:<14} {(bls or '—'):<18} {(mit or '—'):<18} {census or '—'}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="mainstreet",
        description="Main Street — Public policy hedonic assessment",
    )
    sub = parser.add_subparsers(dest="command")

    p_tb = sub.add_parser("time-budget", help="Show ATUS time budget (how Americans spend their day)")
    p_tb.add_argument("--all-persons", action="store_true", help="Show all persons (default: employed)")

    p_bls = sub.add_parser("bls", help="Fetch real BLS data")
    p_bls.add_argument("series", help="Series name or BLS ID (run 'mainstreet series' to list)")

    sub.add_parser("series", help="List available BLS series")
    sub.add_parser("domains", help="Show hedonic domains with federal data mappings")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands = {
        "time-budget": cmd_time_budget,
        "bls": cmd_bls,
        "series": cmd_series,
        "domains": cmd_domains,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
