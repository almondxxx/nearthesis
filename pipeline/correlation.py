"""Correlation dashboard data: does a rise in NEAR Intents volume go with, or
come before, a rise in NEAR adoption metrics?  -> docs/data/correlation.json

All tests use weekly log growth (complete Mon-Sun weeks), so two series that
merely trend over the same two years cannot look related. The week containing
the 2026-04-02 break (one large automated sender stopping) and the week after
it are excluded from every growth statistic; level correlations are shown only as a warning example.

Views per (Intents measure, adoption metric):
  lead_lag   r between Intents growth at t and metric growth at t+k, k = -8..+8
             (k > 0: Intents moves first; k < 0: the metric moves first)
  scatter    same-week growth pairs, with OLS slope
  rolling    26-week rolling same-week correlation
  quartiles  mean next-week metric growth after the top vs bottom quartile of
             Intents growth weeks (Welch t-test)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from pipeline import hypothesis as H
from pipeline.thesis import assemble

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "docs" / "data" / "correlation.json"
MAXK = 8
ROLL = 26

METRICS = {  # column -> (label, weekly aggregation, source note)
    "active_accounts": ("Active accounts", "mean", "daily distinct signers"),
    "transactions": ("Transactions", "mean", "daily transactions"),
    "new_accounts": ("New accounts", "mean", "accounts created per day (NearBlocks)"),
    "returning_accounts": ("Returning accounts", "mean", "active minus new (NearBlocks)"),
    "fees_native": ("Fees burned (NEAR)", "sum", "transaction fees in NEAR (NearBlocks)"),
    "contract_calls": ("Contract calls", "mean", "function-call receipts (BigQuery)"),
}
MEASURES = {"intents_usd": "NEAR Intents volume (USD)", "intents_swaps": "NEAR Intents swaps (sampled)"}


def _weekly() -> tuple[pd.DataFrame, dict]:
    df, meta = assemble()
    nb = pd.read_csv(RAW / "near_nearblocks.csv", parse_dates=["date"], index_col="date")
    df["new_accounts"] = nb["new_accounts"]
    df["returning_accounts"] = (nb["active_accounts"] - nb["new_accounts"]).clip(lower=0)
    how = {c: a for c, (_, a, _) in METRICS.items()}
    how.update({"intents_usd": "sum", "btc_price": "mean"})
    w = H.weekly(df, how)
    if (RAW / "intents_hour_samples.csv").exists():
        s = pd.read_csv(RAW / "intents_hour_samples.csv", parse_dates=["date"]).drop_duplicates(["date", "hour"])
        g = s.set_index("date")["swaps_success"].resample("W-SUN")
        sw = (g.mean() * 168).where(g.count() >= 7).reindex(w.index)
        if sw.notna().sum() >= 30:
            w["intents_swaps"] = sw
    return w, meta


def _clean_growth(w: pd.DataFrame) -> pd.DataFrame:
    g = H.growth(w)
    brk = H.break_dummy(g.index)
    return g[brk == 0]  # drop the documented break week


def _r(x, y):
    d = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(d) < 20:
        return None, None, len(d)
    r, p = stats.pearsonr(d.x, d.y)
    return round(float(r), 3), round(float(p), 4), len(d)


def pair(g: pd.DataFrame, w: pd.DataFrame, x: str, y: str) -> dict:
    ll = []
    for k in range(-MAXK, MAXK + 1):
        r, p, n = _r(g[x], g[y].shift(-k))
        ll.append({"k": k, "r": r, "p": p, "n": n})
    d = pd.DataFrame({"x": g[x], "y": g[y]}).dropna()
    slope = float(np.polyfit(d.x, d.y, 1)[0]) if len(d) > 10 else None
    roll = g[x].rolling(ROLL, min_periods=ROLL).corr(g[y])
    # next-week response after strong vs weak Intents weeks
    nd = pd.DataFrame({"x": g[x], "y_next": g[y].shift(-1)}).dropna()
    q_hi, q_lo = nd.x.quantile(0.75), nd.x.quantile(0.25)
    hi, lo = nd.y_next[nd.x >= q_hi], nd.y_next[nd.x <= q_lo]
    t = stats.ttest_ind(hi, lo, equal_var=False) if len(hi) > 3 and len(lo) > 3 else None
    lv = np.log(w[[x, y]].where(w[[x, y]] > 0)).dropna()
    level_r = round(float(lv[x].corr(lv[y])), 3) if len(lv) > 20 else None
    same = next(c for c in ll if c["k"] == 0)
    sig = lambda c: c["p"] is not None and c["p"] < 0.05
    # an "increase leads to an increase" needs a POSITIVE significant correlation;
    # significant negative ones are reported separately as reversals
    lead = [c for c in ll if c["k"] >= 1 and sig(c) and c["r"] > 0]
    lag = [c for c in ll if c["k"] <= -1 and sig(c) and c["r"] > 0]
    rev = [c for c in ll if c["k"] != 0 and sig(c) and c["r"] < 0]
    return {
        "lead_lag": ll,
        "scatter": {"x": [round(float(v), 4) for v in d.x], "y": [round(float(v), 4) for v in d.y],
                    "date": [i.strftime("%Y-%m-%d") for i in d.index], "slope": None if slope is None else round(slope, 4)},
        "rolling": [None if pd.isna(v) else round(float(v), 3) for v in roll.reindex(w.index)],
        "quartiles": {"after_top": None if hi.empty else round(float(hi.mean()), 4),
                      "after_bottom": None if lo.empty else round(float(lo.mean()), 4),
                      "n_top": int(len(hi)), "n_bottom": int(len(lo)),
                      "p": None if t is None else round(float(t.pvalue), 4)},
        "level_r": level_r,
        "same_week": same,
        "sig_leads": [c["k"] for c in lead],
        "sig_lags": [c["k"] for c in lag],
        "reversals": [c["k"] for c in rev],
        "verdict": _verdict(same, lead, lag),
    }


def _verdict(same, lead, lag) -> str:
    together = same["p"] is not None and same["p"] < 0.05
    base = ("Move together (same week)" if same["r"] > 0 else "Move in opposite directions (same week)") if together else None
    extra = []
    if lead:
        extra.append("Intents moves first")
    if lag:
        extra.append("metric moves first")
    if base and extra:
        return f"{base}; {', '.join(extra)}"
    if base:
        return base
    if extra:
        return "; ".join(extra).capitalize()
    return "No reliable link"


def _sentence(xl, yl, r: dict) -> str:
    s, q = r["same_week"], r["quartiles"]
    parts = []
    if s["r"] is not None:
        pv = "p < 0.001" if s["p"] < 0.001 else f"p = {s['p']:.3f}"
        parts.append(f"Same week: r = {s['r']:+.2f} ({'significant' if s['p'] < 0.05 else 'not significant'}, {pv}).")
    parts.append(f"Intents rising before the metric rises (positive leads at 1-{MAXK} weeks): {', '.join(f'k={k}' for k in r['sig_leads']) or 'none'}.")
    if r["reversals"]:
        parts.append(f"Significant negative links at k = {', '.join(str(k) for k in r['reversals'])}: a bounce-back pattern, not a lead.")
    if q["after_top"] is not None:
        parts.append(f"After the strongest quarter of Intents weeks, {yl[0].lower() + yl[1:]} grew {q['after_top']*100:+.1f}% the next week, "
                     f"versus {q['after_bottom']*100:+.1f}% after the weakest (p = {q['p']:.2f}).")
    return " ".join(parts)


def build() -> dict:
    w, meta = _weekly()
    g = _clean_growth(w)
    metrics = [m for m in METRICS if m in w and w[m].notna().sum() >= 30]
    measures = [m for m in MEASURES if m in w and w[m].notna().sum() >= 30]
    pairs = {}
    for x in measures:
        for y in metrics:
            r = pair(g, w, x, y)
            r["sentence"] = _sentence(MEASURES[x], METRICS[y][0], r)
            pairs[f"{x}|{y}"] = r
    out = {
        "meta": {"built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "first_week": w.index[0].strftime("%Y-%m-%d"), "last_week": w.index[-1].strftime("%Y-%m-%d"),
                 "weeks": int(len(w)), "max_k": MAXK, "rolling_weeks": ROLL,
                 "usage_source": meta.get("usage_source"), "bq_available": meta.get("bq_available"),
                 "break_days": H.BREAK_DAYS,
                 "metrics": {m: {"label": METRICS[m][0], "source": METRICS[m][2]} for m in metrics},
                 "measures": {m: MEASURES[m] for m in measures},
                 "not_available": [METRICS[m][0] for m in METRICS if m not in metrics]},
        "weeks": [d.strftime("%Y-%m-%d") for d in w.index],
        "levels": {c: [None if pd.isna(v) else round(float(v), 2) for v in w[c]] for c in metrics + measures},
        "pairs": pairs,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, separators=(",", ":"), allow_nan=False))
    return out
