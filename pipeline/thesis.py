"""Build docs/data/thesis.json and reports/thesis_results.md for the
hypothesis test. Every chart carries: its data, the exact query/API call behind
it, and one plain sentence computed from the data (never typed by hand).
A metric whose source is unavailable is marked "not computed", never filled.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline import bq, hypothesis as H, intents

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "docs" / "data" / "thesis.json"
REPORT = ROOT / "reports" / "thesis_results.md"
START = pd.Timestamp("2024-12-01")  # first full month of NEAR Intents data on DefiLlama

NEARBLOCKS_Q = "GET https://api.nearblocks.io/v1/charts  ->  fields: {f}  (daily, public, no key)"
LLAMA_Q = "GET https://api.llama.fi/summary/dexs/near-intents  ->  totalDataChart (daily USD volume, public, no key)"
BTC_Q = "GET https://coins.llama.fi/chart/coingecko:bitcoin?period=1d  (daily price, public, no key)"
EXPLORER_Q = ("GET https://explorer.near-intents.org/api/v0/transactions"
              "?startTimestampUnix=<hour start>&endTimestampUnix=<hour end>&numberOfTransactions=1000\n"
              "Authorization: Bearer $NEAR_INTENTS_JWT\n"
              "-> 2 random UTC hours per day (seeded by date), every swap in each hour (paged);\n"
              "   daily swaps = mean(successful swaps per sampled hour) x 24")


def _sql(name: str) -> str:
    return (ROOT / "sql" / name).read_text().strip()


def _r(s: pd.Series, nd=2):
    return [None if (v is None or not np.isfinite(v)) else round(float(v), nd) for v in s]


def _fmt(v):
    if v is None or not np.isfinite(v):
        return "n/a"
    a = abs(v)
    return f"{v/1e9:.2f}B" if a >= 1e9 else f"{v/1e6:.2f}M" if a >= 1e6 else f"{v/1e3:.1f}K" if a >= 1e3 else f"{v:,.2f}"


def _chg(s: pd.Series, days=30):
    s = s.dropna()
    if len(s) < days + 365:
        return None
    now = s.iloc[-days:].mean()
    then = s.loc[s.index[-1] - pd.Timedelta(days=365 + days - 1): s.index[-1] - pd.Timedelta(days=365)].mean()
    return now / then - 1 if then else None


def assemble() -> tuple[pd.DataFrame, dict]:
    nb = pd.read_csv(RAW / "near_nearblocks.csv", parse_dates=["date"], index_col="date")
    ll = pd.read_csv(RAW / "intents_llama.csv", parse_dates=["date"], index_col="date")
    btc = pd.read_csv(RAW / "btc_price.csv", parse_dates=["date"], index_col="date")
    est = intents.daily_estimates()
    df = pd.DataFrame(index=pd.date_range(START, nb.index.max(), freq="D"))
    df["near_price"] = nb["price_usd"]
    df["nb_active_accounts"] = nb["active_accounts"]
    df["nb_transactions"] = nb["txns"]
    df["intents_usd"] = ll["intents_volume_usd_llama"]
    df["btc_price"] = btc["btc_price_usd"]
    if len(est):
        df["intents_swaps"] = est["swaps_est"]
        df["intents_usd_explorer"] = est["usd_est"]
        df["intents_senders_per_hour"] = est["senders_per_hour"]
        df["intents_sampled_hours"] = est["sampled_hours"]
    meta = {"bq_available": False, "bq_freshness": bq.load_freshness()}
    act, cu = bq.load("bq_daily_activity"), bq.load("bq_contract_usage")
    if act is not None:
        df["bq_active_accounts"] = act["active_accounts"]
        df["bq_transactions"] = act["transactions"]
        meta["bq_available"] = True
        meta["bq_last_day"] = act.index.max().strftime("%Y-%m-%d")
    if cu is not None:
        for c in ["function_calls", "contracts_called", "intents_contract_calls", "intents_contract_callers"]:
            df[f"bq_{c}"] = cu[c]
    today = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize()
    return df[df.index < today], meta


def build() -> dict:
    df, meta = assemble()
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / "thesis_daily.csv", float_format="%.6g")
    yesterday = df.index.max()
    bq_fresh = bool(meta["bq_available"] and pd.Timestamp(meta["bq_last_day"]) >= yesterday - pd.Timedelta(days=7))
    meta["bq_fresh"] = bq_fresh

    # ---------------- targets: BigQuery when fresh, else NearBlocks (labelled)
    if bq_fresh:
        targets = {"bq_active_accounts": "Active accounts (BigQuery)", "bq_transactions": "Transactions (BigQuery)",
                   "bq_function_calls": "Contract calls (BigQuery)", "bq_contracts_called": "Distinct contracts called (BigQuery)"}
    else:
        targets = {"nb_active_accounts": "Active accounts (NearBlocks)", "nb_transactions": "Transactions (NearBlocks)"}
        if meta["bq_available"]:  # stale BigQuery still gives contract usage over its own window
            targets.update({"bq_function_calls": "Contract calls (BigQuery, to its last day)",
                            "bq_contracts_called": "Distinct contracts called (BigQuery, to its last day)"})
    how = {**{t: "mean" for t in targets}, "intents_usd": "sum", "near_price": "mean", "btc_price": "mean"}
    w = H.weekly(df, how)
    # weekly swaps from the sampled hours directly: mean hourly x 168 (more precise than summing days)
    if (RAW / "intents_hour_samples.csv").exists():
        s = pd.read_csv(RAW / "intents_hour_samples.csv", parse_dates=["date"]).drop_duplicates(["date", "hour"])
        g = s.set_index("date")["swaps_success"].resample("W-SUN")
        sw = (g.mean() * 168).where(g.count() >= 7)
        w["intents_swaps"] = sw.reindex(w.index)
        se = (g.std() / np.sqrt(g.count()) * 168).reindex(w.index)
        meta["weekly_swaps_rel_se_median"] = float((se / w["intents_swaps"]).median()) if w["intents_swaps"].notna().any() else None
    w.to_csv(PROCESSED / "thesis_weekly.csv", float_format="%.6g")
    res = H.run(w, targets)

    # ---------------- charts (daily, 7-day average), each with query + sentence
    d7 = df.rolling(7, min_periods=5).mean()
    dates = [x.strftime("%Y-%m-%d") for x in df.index]
    charts = []

    def add(cid, title, series, query, sentence, kind="line", unit="", note=None):
        charts.append({"id": cid, "title": title, "series": series, "query": query,
                       "sentence": sentence, "kind": kind, "unit": unit, "note": note})

    act_col = "bq_active_accounts" if bq_fresh else "nb_active_accounts"
    tx_col = "bq_transactions" if bq_fresh else "nb_transactions"
    act_q = _sql("01_daily_activity.sql") if bq_fresh else NEARBLOCKS_Q.format(f="active_accounts")
    tx_q = _sql("01_daily_activity.sql") if bq_fresh else NEARBLOCKS_Q.format(f="txns")
    a30, ach = df[act_col].iloc[-30:].mean(), _chg(df[act_col])
    add("active", "Daily active accounts", {"Active accounts (7-day avg)": _r(d7[act_col], 0)}, act_q,
        f"NEAR averaged {_fmt(a30)} active accounts a day over the last 30 days"
        + (f", {ach:+.0%} versus the same 30 days a year earlier." if ach is not None else "."))
    t30, tch = df[tx_col].iloc[-30:].mean(), _chg(df[tx_col])
    add("txns", "Daily transactions", {"Transactions (7-day avg)": _r(d7[tx_col], 0)}, tx_q,
        f"NEAR processed {_fmt(t30)} transactions a day over the last 30 days"
        + (f", {tch:+.0%} versus a year earlier." if tch is not None else "."))

    if meta["bq_available"] and "bq_function_calls" in df:
        last = meta["bq_last_day"]
        cc = df["bq_contracts_called"].dropna()
        add("contracts", "Contract usage", {"Contract calls (7-day avg)": _r(d7["bq_function_calls"], 0)},
            _sql("02_contract_usage.sql"),
            f"Up to {last}, NEAR saw {_fmt(df['bq_function_calls'].dropna().iloc[-30:].mean())} contract calls a day "
            f"across {_fmt(cc.iloc[-30:].mean())} distinct contracts (30-day averages).")
        ic = df["bq_intents_contract_calls"].dropna()
        add("intents_onchain", "On-chain calls to intents.near", {"Calls to intents.near (7-day avg)": _r(d7["bq_intents_contract_calls"], 0)},
            _sql("02_contract_usage.sql"),
            f"The intents.near contract received {_fmt(ic.iloc[-30:].mean())} calls a day in the 30 days to {last}.")
    else:
        add("contracts", "Contract usage", {}, _sql("02_contract_usage.sql"),
            "Not computed yet: BigQuery credentials were not available when this page was built.")

    iv = df["intents_usd"].dropna()
    add("intents_usd", "NEAR Intents volume (USD)", {"DefiLlama, complete (7-day avg)": _r(d7["intents_usd"], 0),
        **({"Explorer API, sampled estimate (7-day avg)": _r(d7["intents_usd_explorer"], 0)} if "intents_usd_explorer" in d7 else {})},
        LLAMA_Q + "\n\n" + EXPLORER_Q,
        f"NEAR Intents moved ${_fmt(iv.iloc[-30:].mean())} a day over the last 30 days; "
        f"it moved ${_fmt(iv.iloc[:30].mean())} a day in its first 30 days on DefiLlama ({iv.index[0].date()}).", unit="$")

    if "intents_swaps" in df and df["intents_swaps"].notna().sum() > 30:
        sw = df["intents_swaps"].dropna()
        cover = int(df["intents_sampled_hours"].sum())
        add("intents_swaps", "NEAR Intents swaps per day (sampled)", {"Estimated successful swaps (7-day avg)": _r(d7["intents_swaps"], 0)},
            EXPLORER_Q,
            f"From {cover} sampled hours, NEAR Intents handled about {_fmt(sw.iloc[-30:].mean())} successful swaps a day over the last 30 days.",
            note=f"Estimate from sampled hours; median weekly relative standard error {meta.get('weekly_swaps_rel_se_median', 0):.0%}.")
    else:
        add("intents_swaps", "NEAR Intents swaps per day (sampled)", {}, EXPLORER_Q,
            "Not computed yet: the Explorer API sample has not been collected.")

    base = df[["near_price", "btc_price"]].dropna().iloc[0]
    add("price", "NEAR and BTC price (indexed, first day = 100)",
        {"NEAR": _r(df["near_price"] / base["near_price"] * 100, 1), "BTC (market control)": _r(df["btc_price"] / base["btc_price"] * 100, 1)},
        NEARBLOCKS_Q.format(f="near_price") + "\n" + BTC_Q,
        f"Since {df.index[0].date()}, NEAR's price changed {df['near_price'].dropna().iloc[-1]/base['near_price']-1:+.0%} and BTC's {df['btc_price'].dropna().iloc[-1]/base['btc_price']-1:+.0%}.")

    lv = df[[act_col, "intents_usd"]].dropna()
    b2 = lv.iloc[:30].mean()
    add("levels", "Intents volume vs active accounts (indexed, first 30 days = 100)",
        {"NEAR Intents volume": _r(d7["intents_usd"] / b2["intents_usd"] * 100, 1),
         "Active accounts": _r(d7[act_col] / b2[act_col] * 100, 1)},
        "Derived from the two charts above (same queries).",
        f"Over the whole period Intents volume ended at {lv['intents_usd'].iloc[-30:].mean()/b2['intents_usd']*100:,.0f} "
        f"and active accounts at {lv[act_col].iloc[-30:].mean()/b2[act_col]*100:,.0f} (start = 100): in levels they moved "
        + ("in opposite directions." if (lv['intents_usd'].iloc[-30:].mean() > b2['intents_usd']) != (lv[act_col].iloc[-30:].mean() > b2[act_col]) else "the same way."),
        kind="log")

    out = {
        "meta": {**meta, "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "as_of": df.index.max().strftime("%Y-%m-%d"), "start": df.index[0].strftime("%Y-%m-%d"),
                 "targets": targets, "predictors": H.PREDICTORS, "lags": H.LAGS, "max_lead": H.MAX_LEAD, "alpha": H.ALPHA,
                 "weeks": int(len(w))},
        "dates": dates, "charts": charts, "test": res,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, separators=(",", ":"), allow_nan=False, default=str))
    _report(out)
    return out


def _report(o: dict) -> None:
    m, t = o["meta"], o["test"]
    L = ["# Hypothesis test - latest results", "",
         f"_Generated by `python run.py` on {m['built_at']}; data {m['start']} to {m['as_of']} ({m['weeks']} complete weeks). "
         "Do not edit by hand._", "",
         "**Hypothesis:** cross-chain volume through NEAR Intents is a better leading indicator of real network usage than token price.", "",
         f"## Overall: **{t['overall']}** (Intents won {t['tally'].get('intents', 0)}, price won {t['tally'].get('price', 0)}, "
         f"neither {t['tally'].get('neither', 0)} of {t['n_targets']} usage measures)", "",
         "| Usage measure | Winner | Best Intents measure | Intents p | Intents OOS ratio | Price p | Price OOS ratio |",
         "|---|---|---|---:|---:|---:|---:|"]
    for k, v in t["verdicts"].items():
        L.append(f"| {m['targets'][k]} | {v['winner']} | {v['best_intents_measure']} | {v['intents_p']} | {v['intents_oos_ratio']} | {v['price_p']} | {v['price_oos_ratio']} |")
    L += ["", "p = in-sample F-test that 2 weekly lags of the predictor add nothing (controls: own lags, BTC). "
          "OOS ratio = out-of-sample RMSE with the predictor / without it (< 1 = it helps forecast next week).", "",
          "## Lead-lag correlations (weekly growth; r at lag k = predictor this week vs usage k weeks later)", ""]
    for k, res in t["results"].items():
        L.append(f"### {m['targets'][k]}")
        L.append("| Predictor | " + " | ".join(f"k={i}" for i in range(m["max_lead"] + 1)) + " |")
        L.append("|---|" + "---:|" * (m["max_lead"] + 1))
        for x, r in res.items():
            L.append(f"| {m['predictors'][x]} | " + " | ".join("n/a" if c["r"] is None else (f"**{c['r']}**" if c["p"] < 0.05 else f"{c['r']}") for c in r["lead_lag"]) + " |")
        L.append("")
    L += ["Bold = p < 0.05.", "", "## Data availability", ""]
    fr = m.get("bq_freshness")
    if not m["bq_available"]:
        L.append("- BigQuery: **not computed** - no credentials were available when this report was built. Usage targets use NearBlocks.")
    else:
        L.append(f"- BigQuery data runs to {m.get('bq_last_day')} (freshness check: {fr}). Fresh enough for the main test: {m['bq_fresh']}.")
    REPORT.write_text("\n".join(L) + "\n")
