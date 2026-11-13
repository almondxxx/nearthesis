"""NEAR Intents Explorer API: sampled swap counts.

The Explorer API (https://explorer.near-intents.org/api/v0, 1Click swaps only)
allows 1 request every 5 seconds and returns at most 1000 swaps per request.
At ~30k swaps/day a full history would take ~36 hours, so we SAMPLE:

  * every day gets SAMPLE_HOURS random UTC hours (seeded by the date, so the
    sample is reproducible);
  * every swap in each sampled hour is fetched (paging if > 1000);
  * days are visited in a fixed random order, so an interrupted run still
    covers the whole period evenly; the run is resumable from the cache.

Daily swaps are estimated as mean(sampled hourly count) x 24. The hours are
picked uniformly, so the estimate is unbiased; its error is reported.
Unique senders cannot be scaled from hours to days, so they are reported per
sampled hour only (an activity index, not a daily user count).

Needs NEAR_INTENTS_JWT (from https://partners.near-intents.org) in the
environment or in .env. Without it, the committed cache is used as-is.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "raw" / "intents_hour_samples.csv"
URL = "https://explorer.near-intents.org/api/v0/transactions"
SAMPLE_HOURS = 2
START = pd.Timestamp("2025-01-01")
MIN_GAP = 5.2  # seconds between requests (API: 1 request / 5 s)

COLUMNS = ["date", "hour", "swaps_all", "swaps_success", "swaps_refunded", "swaps_failed",
           "usd_in_success", "unique_senders", "pages", "fetched_at"]


def _token() -> str | None:
    tok = os.environ.get("NEAR_INTENTS_JWT")
    if tok:
        return tok.strip()
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.strip().startswith("NEAR_INTENTS_JWT="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


class Client:
    def __init__(self, token: str):
        self.s = requests.Session()
        self.s.headers["Authorization"] = f"Bearer {token}"
        self.last = 0.0

    def get(self, params: dict) -> list:
        for attempt in range(6):
            wait = MIN_GAP - (time.time() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()
            try:
                r = self.s.get(URL, params=params, timeout=90)
            except requests.RequestException:
                time.sleep(10 * (attempt + 1))
                continue
            if r.status_code == 429:
                time.sleep(15 * (attempt + 1))
                continue
            if r.status_code >= 500:
                time.sleep(10 * (attempt + 1))
                continue
            r.raise_for_status()
            return r.json()
        raise RuntimeError("Explorer API kept failing")


def sample_hours(day: pd.Timestamp, k: int = SAMPLE_HOURS) -> list[int]:
    rng = np.random.default_rng(int(day.strftime("%Y%m%d")))
    return sorted(int(h) for h in rng.choice(24, size=k, replace=False))


def fetch_hour(c: Client, day: pd.Timestamp, hour: int) -> dict:
    start = int((day + pd.Timedelta(hours=hour)).timestamp())
    params = {"numberOfTransactions": 1000, "startTimestampUnix": start, "endTimestampUnix": start + 3600 - 1}
    base = dict(params)
    rows, pages, prev_first = [], 0, None
    while True:
        page = c.get(params)
        pages += 1
        if not page:
            break
        first = (page[0].get("depositAddress"), page[0].get("createdAt"))
        if first == prev_first or pages > 40:  # cursor did not advance: stop, never loop
            raise RuntimeError(f"Explorer pagination stalled for {day.date()} {hour:02d}h")
        prev_first = first
        rows += page
        if len(page) < 1000:
            break
        last = page[-1]
        # Send the memo only when the swap has one: an empty memo makes the API repeat the page.
        params = {**base, "lastDepositAddress": last["depositAddress"], "direction": "next"}
        if last.get("depositMemo"):
            params["lastDepositMemo"] = last["depositMemo"]
    seen, uniq = set(), []
    for r in rows:  # guard against overlapping pages
        key = (r.get("depositAddress"), r.get("depositMemo"), r.get("createdAt"))
        if key not in seen:
            seen.add(key)
            uniq.append(r)
    st = pd.Series([r.get("status") for r in uniq], dtype="object")
    ok = [r for r in uniq if r.get("status") == "SUCCESS"]
    senders = {(r.get("senders") or [None])[0] for r in ok} - {None}
    return {
        "date": day.strftime("%Y-%m-%d"), "hour": hour,
        "swaps_all": len(uniq), "swaps_success": len(ok),
        "swaps_refunded": int((st == "REFUNDED").sum()), "swaps_failed": int((st == "FAILED").sum()),
        "usd_in_success": round(sum(float(r.get("amountInUsd") or 0) for r in ok), 2),
        "unique_senders": len(senders), "pages": pages,
        "fetched_at": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def run(max_minutes: float | None = None, end: pd.Timestamp | None = None) -> int:
    """Fill missing sampled hours in the cache. Returns how many hours were fetched."""
    tok = _token()
    if not tok:
        print("intents: NEAR_INTENTS_JWT not set - using the committed cache only")
        return 0
    end = end or (pd.Timestamp.now(tz="UTC").tz_localize(None).normalize() - pd.Timedelta(days=1))
    days = pd.date_range(START, end, freq="D")
    done = set()
    if CACHE.exists():
        old = pd.read_csv(CACHE, dtype={"date": str})
        done = set(zip(old["date"], old["hour"].astype(int)))
    order = np.random.default_rng(7).permutation(len(days))  # even coverage even if interrupted
    todo = [(days[i], h) for i in order for h in sample_hours(days[i])
            if (days[i].strftime("%Y-%m-%d"), h) not in done]
    # newest days first among the latest week, so the daily refresh keeps "today" current
    recent = [t for t in todo if t[0] >= end - pd.Timedelta(days=7)]
    todo = recent + [t for t in todo if t not in recent]
    print(f"intents: {len(done)} sampled hours cached, {len(todo)} to fetch", flush=True)
    c, t0, n = Client(tok), time.time(), 0
    write_header = not CACHE.exists()
    with CACHE.open("a") as fh:
        if write_header:
            fh.write(",".join(COLUMNS) + "\n")
        for day, hour in todo:
            if max_minutes and (time.time() - t0) / 60 > max_minutes:
                print("intents: time budget reached, stopping (resumable)")
                break
            row = fetch_hour(c, day, hour)
            fh.write(",".join(str(row[k]) for k in COLUMNS) + "\n")
            fh.flush()
            n += 1
            if n % 25 == 0:
                print(f"intents: {n}/{len(todo)} hours fetched", flush=True)
    return n


def daily_estimates() -> pd.DataFrame:
    """Per-day estimate of swaps from the sampled hours (x24), with sampling error."""
    if not CACHE.exists():
        return pd.DataFrame()
    s = pd.read_csv(CACHE, parse_dates=["date"]).drop_duplicates(["date", "hour"], keep="last")
    g = s.groupby("date")
    out = pd.DataFrame({
        "sampled_hours": g.size(),
        "swaps_est": g["swaps_success"].mean() * 24,
        "swaps_all_est": g["swaps_all"].mean() * 24,
        "usd_est": g["usd_in_success"].mean() * 24,
        "senders_per_hour": g["unique_senders"].mean(),
        "hourly_sd": g["swaps_success"].std(ddof=1),
    })
    out.index.name = "date"
    return out.sort_index()


if __name__ == "__main__":
    import sys
    mins = float(sys.argv[1]) if len(sys.argv) > 1 else None
    run(max_minutes=mins)
