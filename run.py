#!/usr/bin/env python3
"""Rebuild every chart from raw data - one command.

    python run.py                      # fetch fresh data, then rebuild everything
    python run.py --offline            # rebuild from the committed data/raw/ only
    python run.py --intents-minutes 30 # cap time spent sampling the Explorer API

Sources and keys (keys are optional; without one, that source's committed cache is used):
  NearBlocks, DefiLlama, NEAR RPC, CoinGecko, Avalanche Data API   public, no key
  BigQuery  bigquery-public-data.crypto_near_mainnet_us            GCP_SA_KEY_B64 | GCP_SA_KEY_JSON | GOOGLE_APPLICATION_CREDENTIALS
  NEAR Intents Explorer API                                        NEAR_INTENTS_JWT (env or .env)

Outputs: docs/data/thesis.json + reports/thesis_results.md   (main thesis: Intents vs usage)
         docs/data/dashboard.json + reports/latest.md        (appendix: valuation)
"""
import argparse
import sys

from pipeline import bq, intents
from pipeline.build import build
from pipeline.sources import fetch_all
from pipeline.thesis import build as build_thesis
from pipeline.correlation import build as build_correlation


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="skip fetching; use data/raw/ as committed")
    ap.add_argument("--intents-minutes", type=float, default=20.0,
                    help="max minutes to spend sampling the Explorer API this run (default 20; 0 = skip)")
    args = ap.parse_args()
    if not args.offline:
        fetch_all()
        try:
            bq.fetch_all()
        except Exception as e:  # keep the build going on the cached BigQuery CSVs
            print(f"bq: FAILED ({e}) - using cached BigQuery CSVs", file=sys.stderr)
        if args.intents_minutes > 0:
            try:
                intents.run(max_minutes=args.intents_minutes)
            except Exception as e:
                print(f"intents: FAILED ({e}) - using the cached sample", file=sys.stderr)

    t = build_thesis()
    a = t["results"]["answers"]
    print(f"thesis: {t['meta']['start']} to {t['meta']['as_of']}, {t['meta']['weeks']} weeks -> "
          f"Q1 {a['Q1']} | Q2 {a['Q2']} | Q3 {a['Q3']}")
    c = build_correlation()
    print(f"correlation: {len(c['pairs'])} Intents/adoption pairs -> docs/data/correlation.json")
    out = build()
    print(f"appendix: NEAR valuation verdict {out['near']['verdict']} (as of {out['meta']['as_of']})")
    print("wrote docs/data/thesis.json, reports/thesis_results.md, docs/data/dashboard.json, reports/latest.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
