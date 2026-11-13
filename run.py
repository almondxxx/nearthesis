#!/usr/bin/env python3
"""NEAR investment-thesis pipeline.

    python run.py            # fetch fresh public data, then build everything
    python run.py --offline  # rebuild from the committed snapshot in data/raw/

Outputs: data/processed/*.csv, docs/data/dashboard.json, reports/latest.md
"""
import argparse
import sys

from pipeline.build import build
from pipeline.sources import fetch_all


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="skip fetching; use data/raw/ as committed")
    args = ap.parse_args()
    if not args.offline:
        fetch_all()
    out = build()
    L = out["latest"]
    print(f"as of {out['meta']['as_of']}")
    for c in ("near", "avax"):
        print(f"  {c.upper():4}  fundamentals {L[c]['fundamentals']:>5}  valuation {L[c]['valuation']:>5}  "
              f"confidence premium {L[c]['confidence_premium']:>6}")
    print("wrote docs/data/dashboard.json and reports/latest.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
