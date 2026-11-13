"""Run the SQL in sql/ against bigquery-public-data.crypto_near_mainnet_us.

* Credentials, first match wins:
    GCP_SA_KEY_B64                  base64 of the service-account JSON (cloud env vars)
    GCP_SA_KEY_JSON                 the raw JSON (GitHub Actions secret)
    GOOGLE_APPLICATION_CREDENTIALS  path to the key file (local machine)
  The key's own project is billed. Without credentials the committed CSVs are used.
* Every query is dry-run first; it is refused if it would scan more than
  BQ_MAX_GB (default 150 GB; BigQuery's free tier is 1 TB/month).
* Incremental: only dates after the last cached day are queried.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SQL = ROOT / "sql"
RAW = ROOT / "data" / "raw"
START = pd.Timestamp("2024-11-01")  # covers the Intents era plus a warm-up month
MAX_GB = float(os.environ.get("BQ_MAX_GB", "150"))

QUERIES = {  # cache file -> sql file
    "bq_daily_activity": "01_daily_activity.sql",
    "bq_contract_usage": "02_contract_usage.sql",
    "bq_returning_signers": "03_weekly_returning_signers.sql",   # weekly rows, block_date = Sunday
}


def _client():
    info = None
    if os.environ.get("GCP_SA_KEY_B64"):
        info = json.loads(base64.b64decode(os.environ["GCP_SA_KEY_B64"]).decode("utf-8"))
    elif os.environ.get("GCP_SA_KEY_JSON"):
        info = json.loads(os.environ["GCP_SA_KEY_JSON"])
    elif not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        return None
    from google.cloud import bigquery
    from google.oauth2 import service_account
    if info:
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/cloud-platform"])
        return bigquery.Client(credentials=creds, project=info["project_id"])
    return bigquery.Client()


def _run(client, sql_file: str, params: dict | None = None) -> pd.DataFrame:
    from google.cloud import bigquery
    sql = (SQL / sql_file).read_text()
    qp = [bigquery.ScalarQueryParameter(k, "DATE", v) for k, v in (params or {}).items()]
    dry = client.query(sql, job_config=bigquery.QueryJobConfig(query_parameters=qp, dry_run=True, use_query_cache=False))
    gb = dry.total_bytes_processed / 1e9
    print(f"bq: {sql_file} {params or ''} would scan {gb:.2f} GB", flush=True)
    if gb > MAX_GB:
        raise RuntimeError(f"{sql_file} would scan {gb:.1f} GB > BQ_MAX_GB={MAX_GB}; narrow the dates or raise the cap")
    job = client.query(sql, job_config=bigquery.QueryJobConfig(query_parameters=qp))
    rows = [dict(r.items()) for r in job.result()]  # no db-dtypes / pyarrow dependency
    print(f"bq: {sql_file} -> {len(rows)} rows, billed {(job.total_bytes_billed or 0) / 1e9:.2f} GB", flush=True)
    return pd.DataFrame(rows)


def freshness(client) -> dict:
    df = _run(client, "00_freshness.sql")
    out = {r.table_name: {"latest": pd.to_datetime(r.latest_partition, format="%Y%m%d").strftime("%Y-%m-%d"),
                          "rows": int(r.total_rows)} for r in df.itertuples()}
    out["checked_at"] = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    (RAW / "bq_freshness.json").write_text(json.dumps(out, indent=1))
    return out


def fetch_all() -> bool:
    client = _client()
    if client is None:
        print("bq: no GCP credentials - using committed BigQuery CSVs")
        return False
    fr = freshness(client)
    print(f"bq: freshness {fr}", flush=True)
    try:
        _run(client, "04_schema.sql").to_csv(RAW / "bq_schema.csv", index=False)
    except Exception as e:
        print(f"bq: schema check FAILED ({e})", flush=True)
    latest = min(pd.Timestamp(v["latest"]) for k, v in fr.items() if k != "checked_at")
    yesterday = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize() - pd.Timedelta(days=1)
    end = min(latest, yesterday)
    ok = True
    for name, sql_file in QUERIES.items():
        try:
            _fetch_one(client, name, sql_file, end)
        except Exception as e:  # one failing query must not skip the others
            ok = False
            print(f"bq: {name} FAILED ({e}) - keeping its cached CSV", flush=True)
    return ok


def _fetch_one(client, name: str, sql_file: str, end: pd.Timestamp) -> None:
    if True:
        path = RAW / f"{name}.csv"
        old = pd.read_csv(path, parse_dates=["block_date"]) if path.exists() else None
        start = (old["block_date"].max() + pd.Timedelta(days=1)) if old is not None and len(old) else START
        if start > end:
            print(f"bq: {name} up to date ({end.date()})")
            return
        # chunk by ~6 months so each dry run stays well under the cap
        parts = [] if old is None else [old]
        for s in pd.date_range(start, end, freq="183D"):
            e = min(s + pd.Timedelta(days=182), end)
            parts.append(_run(client, sql_file, {"start_date": s.date(), "end_date": e.date()}))
        df = pd.concat(parts, ignore_index=True)
        df["block_date"] = pd.to_datetime(df["block_date"])
        df.drop_duplicates("block_date", keep="last").sort_values("block_date").to_csv(path, index=False)
        print(f"bq: {name} -> {path.name} ({len(df)} rows)")


def load(name: str) -> pd.DataFrame | None:
    path = RAW / f"{name}.csv"
    if not path.exists():
        return None
    return pd.read_csv(path, parse_dates=["block_date"]).set_index("block_date").sort_index()


def load_freshness() -> dict | None:
    p = RAW / "bq_freshness.json"
    return json.loads(p.read_text()) if p.exists() else None


if __name__ == "__main__":
    fetch_all()
