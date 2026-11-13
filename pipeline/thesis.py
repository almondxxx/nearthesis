"""Build docs/data/thesis.json and reports/thesis_results.md for the three
questions in pipeline/hypothesis.py. Every chart carries its data, the exact
query/API call behind it, and one plain sentence computed from the data.
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
START = pd.Timestamp("2024-12-09")  # first Monday after NEAR Intents appears on DefiLlama (2024-12-10)

NEARBLOCKS_Q = "GET https://api.nearblocks.io/v1/charts  ->  fields: {f}  (daily, public, no key)"
LLAMA_Q = "GET https://api.llama.fi/summary/dexs/near-intents  ->  totalDataChart (daily USD volume, public, no key)"
BTC_Q = "GET https://coins.llama.fi/chart/coingecko:bitcoin?period=1d  (daily price, public, no key)"
EXPLORER_Q = ("GET https://explorer.near-intents.org/api/v0/transactions"
              "?startTimestampUnix=<hour start>&endTimestampUnix=<hour end>&numberOfTransactions=1000\n"
              "Authorization: Bearer $NEAR_INTENTS_JWT\n"
              "-> 2 random UTC hours per day (seeded by date), every swap in each hour (paged);\n"
              "   swaps = mean(successful swaps per sampled hour) x 24 per day, x 168 per week")
LABELS = {"active_accounts": "Active accounts", "transactions": "Transactions", "contract_calls": "Contracts/accounts used",
          "adoption": "Adoption Index", "intents_usd": "NEAR Intents volume (USD)",
          "intents_swaps": "NEAR Intents swaps (sampled)", "near_price": "NEAR price",
          "fees_native": "Fees burned (NEAR)", "fees_usd": "Fees (USD)", "returning_signers": "Returning signers (BigQuery)",
          "real_usage": "Real Usage Index"}


def _sql(name: str) -> str:
    return (ROOT / "sql" / name).read_text().strip()


def _r(s: pd.Series, nd=2):
    return [None if (v is None or not np.isfinite(v)) else round(float(v), nd) for v in s]


def _fmt(v):
    if v is None or not np.isfinite(v):
        return "n/a"
    a = abs(v)
    return f"{v/1e9:.2f}B" if a >= 1e9 else f"{v/1e6:.2f}M" if a >= 1e6 else f"{v/1e3:.1f}K" if a >= 1e3 else f"{v:,.2f}"


def assemble() -> tuple[pd.DataFrame, dict]:
    nb = pd.read_csv(RAW / "near_nearblocks.csv", parse_dates=["date"], index_col="date")
    ll = pd.read_csv(RAW / "intents_llama.csv", parse_dates=["date"], index_col="date")
    btc = pd.read_csv(RAW / "btc_price.csv", parse_dates=["date"], index_col="date")
    df = pd.DataFrame(index=pd.date_range(START, nb.index.max(), freq="D"))
    df["near_price"] = nb["price_usd"]
    df["fees_native"] = nb["fees_native"]
    df["fees_usd"] = nb["fees_usd_nearblocks"]
    df["intents_usd"] = ll["intents_volume_usd_llama"]
    df["btc_price"] = btc["btc_price_usd"]
    est = intents.daily_estimates()
    if len(est):
        df["intents_swaps"] = est["swaps_est"]
        df["intents_usd_explorer"] = est["usd_est"]
        df["intents_sampled_hours"] = est["sampled_hours"]

    meta = {"bq_available": False, "bq_freshness": bq.load_freshness()}
    act, cu = bq.load("bq_daily_activity"), bq.load("bq_contract_usage")
    yesterday = df.index.max()
    bq_fresh = act is not None and act.index.max() >= yesterday - pd.Timedelta(days=7)
    meta["bq_available"] = act is not None
    meta["bq_fresh"] = bool(bq_fresh)
    if act is not None:
        meta["bq_last_day"] = act.index.max().strftime("%Y-%m-%d")
    # Usage: BigQuery when it is current; otherwise NearBlocks for the whole window
    # (never spliced: the two sources define these counts differently).
    if bq_fresh:
        df["active_accounts"] = act["active_accounts"]
        df["transactions"] = act["transactions"]
        meta["usage_source"] = "BigQuery"
    else:
        df["active_accounts"] = nb["active_accounts"]
        df["transactions"] = nb["txns"]
        meta["usage_source"] = "NearBlocks"
    if cu is not None and "distinct_receivers" in cu:
        df["intents_direct_txs"] = cu["intents_direct_txs"]
        if bq_fresh:
            df["contract_calls"] = cu["distinct_receivers"]   # contract usage component of the Adoption Index
    today = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize()
    return df[df.index < today], meta


def build() -> dict:
    df, meta = assemble()
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / "thesis_daily.csv", float_format="%.6g")

    comps = ["active_accounts", "transactions"] + (["contract_calls"] if "contract_calls" in df and df["contract_calls"].notna().sum() > 200 else [])
    meta["adoption_components"] = comps
    how = {"active_accounts": "mean", "transactions": "mean", "contract_calls": "mean",
           "intents_usd": "sum", "near_price": "mean", "btc_price": "mean",
           "fees_native": "sum", "fees_usd": "sum"}
    w = H.weekly(df, how)
    measures = ["intents_usd"]
    if (RAW / "intents_hour_samples.csv").exists():
        s = pd.read_csv(RAW / "intents_hour_samples.csv", parse_dates=["date"]).drop_duplicates(["date", "hour"])
        g = s.set_index("date")["swaps_success"].resample("W-SUN")
        sw = (g.mean() * 168).where(g.count() >= 7).reindex(w.index)
        if sw.notna().sum() >= 30:
            w["intents_swaps"] = sw
            measures.append("intents_swaps")
            se = (g.std() / np.sqrt(g.count()) * 168).reindex(w.index)
            meta["weekly_swaps_rel_se_median"] = round(float((se / sw).median()), 3)
        meta["sampled_hours"] = int(len(s))
    rs = bq.load("bq_returning_signers")
    real = ["fees_native"]
    if rs is not None:
        w["returning_signers"] = rs["returning_signers"].reindex(w.index)
        if w["returning_signers"].notna().mean() > 0.9:      # covers the whole window
            real = ["returning_signers", "fees_native"]
    meta["real_usage_components"] = real
    ms = H.mature_start(df["intents_usd"].dropna())
    res = H.run(w, comps, measures, real=real, mature_from=ms)
    if "returning_signers" in w and "returning_signers" not in real:   # partial coverage: test over BigQuery's window
        res["q12_robustness"]["returning_signers~intents_usd"] = H.q1_q2(H.growth(w), "returning_signers", "intents_usd")
    w["adoption"] = res.pop("adoption_weekly")
    w["real_usage"] = res.pop("real_usage_weekly")
    w.to_csv(PROCESSED / "thesis_weekly.csv", float_format="%.6g")

    # ------------------------------------------------------------- charts
    wk = [d.strftime("%Y-%m-%d") for d in w.index]
    d7 = df.rolling(7, min_periods=5).mean()
    days = [d.strftime("%Y-%m-%d") for d in df.index]
    charts = []

    def add(cid, section, title, x, series, query, sentence, kind="line", unit="", note=None):
        charts.append({"id": cid, "section": section, "title": title, "x": x, "series": series, "query": query,
                       "sentence": sentence, "kind": kind, "unit": unit, "note": note})

    usage_q = _sql("01_daily_activity.sql") if meta["usage_source"] == "BigQuery" else \
        NEARBLOCKS_Q.format(f="active_accounts, txns") + "\n(BigQuery: " + (
            f"data ends {meta.get('bq_last_day')}, so it is not used for the current window)" if meta["bq_available"]
            else "not queried - no credentials at build time)")
    ru = w["real_usage"].dropna()
    ser = {"Real Usage Index": _r(w["real_usage"], 1)}
    for c in real:
        ser[LABELS[c]] = _r(w[c] / w[c].dropna().iloc[0] * 100, 1)
    if "returning_signers" in w and "returning_signers" not in real:
        ser[LABELS["returning_signers"] + " - not in index (partial coverage)"] = _r(w["returning_signers"] / w["returning_signers"].dropna().iloc[0] * 100, 1)
    add("real_usage", "Y", "Real Usage Index - primary target (weekly, first week = 100)", wk, ser,
        NEARBLOCKS_Q.format(f="txn_fee (fees in NEAR)") + "\n\n" + _sql("03_weekly_returning_signers.sql"),
        f"The Real Usage Index ({' and '.join(LABELS[c][0].lower() + LABELS[c][1:] for c in real)}) went from 100 in the week of "
        f"{ru.index[0].date()} to {ru.iloc[-1]:,.1f} in the week of {ru.index[-1].date()}.", kind="log",
        note="Primary target: repeat users and fees actually paid are hard for bots to fake. "
             + ("" if "returning_signers" in real else
                "Returning signers (BigQuery) join the index once BigQuery covers the whole window; until then the index is fees burned in NEAR. ")
             + "'Active minus new accounts' is not used: NearBlocks new accounts can exceed active signers.")
    a = w["adoption"].dropna()
    comp_idx = {LABELS[c]: _r(w[c] / w[c].dropna().iloc[0] * 100, 1) for c in comps}
    add("adoption", "Y", "Broad Adoption Index - secondary target (weekly, first week = 100)", wk,
        {"Adoption Index": _r(w["adoption"], 1), **comp_idx},
        usage_q + ("\n\n" + _sql("02_contract_usage.sql") if "contract_calls" in comps else ""),
        f"The broad Adoption Index ({', '.join(LABELS[c][0].lower() + LABELS[c][1:] for c in comps)}) went from 100 in the week of "
        f"{a.index[0].date()} to {a.iloc[-1]:,.1f} in the week of {a.index[-1].date()}.",
        kind="log",
        note=None if "contract_calls" in comps else
        "Contract usage is not in the index yet: it needs BigQuery data that covers the whole window. "
        "NearBlocks' own contract field is not used because it is dominated by one automated sender (see THESIS.md).")

    iv = df["intents_usd"].dropna()
    add("intents_usd", "X1", "NEAR Intents volume (USD, daily, 7-day average)", days,
        {"DefiLlama (complete)": _r(d7["intents_usd"], 0),
         **({"Explorer API (sampled estimate)": _r(df["intents_usd_explorer"].rolling(7, min_periods=3).mean(), 0)} if "intents_usd_explorer" in df else {})},
        LLAMA_Q + "\n\n" + EXPLORER_Q,
        f"NEAR Intents moved ${_fmt(iv.iloc[-30:].mean())} a day over the last 30 days, against "
        f"${_fmt(iv.iloc[:30].mean())} a day in its first 30 days on DefiLlama.", unit="$", kind="log",
        note="The Explorer API covers 1Click swaps only, a subset of all NEAR Intents volume, and each day is "
             "estimated from 2 sampled hours, so its line sits below DefiLlama's and is noisier. DefiLlama is used in the tests.")
    if "intents_swaps" in w:
        sw = w["intents_swaps"].dropna()
        add("intents_swaps", "X1", "NEAR Intents successful swaps (weekly, sampled)", wk,
            {"Estimated swaps per week": _r(w["intents_swaps"], 0)}, EXPLORER_Q,
            f"From {meta['sampled_hours']} sampled hours: about {_fmt(sw.iloc[-4:].mean())} successful swaps a week "
            f"in the last 4 weeks, against {_fmt(sw.iloc[:4].mean())} in the first 4 sampled weeks.",
            note=f"Estimate from 2 random hours per day; median weekly relative standard error "
                 f"{meta.get('weekly_swaps_rel_se_median', 0):.0%}.")
    else:
        add("intents_swaps", "X1", "NEAR Intents successful swaps (weekly, sampled)", wk, {}, EXPLORER_Q,
            "Not computed yet: fewer than 30 weeks of the Explorer API sample have been collected.")

    p0 = df[["near_price", "btc_price"]].dropna().iloc[0]
    add("price", "X2", "NEAR price, with BTC as the market control (indexed, first day = 100)", days,
        {"NEAR": _r(df["near_price"] / p0["near_price"] * 100, 1), "BTC": _r(df["btc_price"] / p0["btc_price"] * 100, 1)},
        NEARBLOCKS_Q.format(f="near_price") + "\n" + BTC_Q,
        f"Since {df.index[0].date()}, NEAR's price changed {df['near_price'].dropna().iloc[-1]/p0['near_price']-1:+.0%} and BTC's "
        f"{df['btc_price'].dropna().iloc[-1]/p0['btc_price']-1:+.0%}.")

    q3 = res["q3"]
    fn = df["fees_native"].dropna()
    add("fees", "V", "Fees burned on NEAR (NEAR per day, 7-day average)", days,
        {"Fees (NEAR)": _r(d7["fees_native"], 1)}, NEARBLOCKS_Q.format(f="txn_fee (yoctoNEAR / 1e24)"),
        f"NEAR users paid {_fmt(fn.iloc[-30:].mean())} NEAR a day in fees over the last 30 days, against "
        f"{_fmt(fn.iloc[:30].mean())} NEAR a day at the start of the window.",
        note="2 April 2026: transactions -72% and fees -62% in one day while active accounts barely moved, "
             "consistent with one large automated sender stopping. That week and the next get a dummy in every test.")
    cap = (w["fees_usd"] / w["intents_usd"] * 1e6).replace([np.inf, -np.inf], np.nan)
    add("capture", "V", "NEAR fees per $1M of NEAR Intents volume (weekly)", wk,
        {"Fees (USD) per $1M Intents volume": _r(cap, 2)},
        NEARBLOCKS_Q.format(f="txn_fee_usd") + "\n" + LLAMA_Q,
        (f"Since Intents passed $1M a day, NEAR's fees per $1M of Intents volume fell from "
         f"${q3['capture_post_launch_first']:,.0f} in {q3['capture_post_launch_from']} to "
         f"${q3['capture_post_launch_last']:,.0f} in {q3['capture_post_launch_to']} "
         f"({q3['capture_post_launch_change']:+.0%}, complete quarters)." if q3.get("capture_post_launch_from") else
         f"In {q3.get('capture_first_q_label')} NEAR earned ${q3.get('capture_first_q')} in fees per $1M of Intents volume; "
         f"in {q3.get('capture_last_q_label')} it earned ${q3.get('capture_last_q')}."), kind="log", unit="$",
        note="Earlier weeks are Intents' launch period, when its volume was tiny, so the ratio there is not comparable.")

    out = {
        "meta": {**meta, "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "as_of": df.index.max().strftime("%Y-%m-%d"), "start": df.index[0].strftime("%Y-%m-%d"),
                 "weeks": int(w["real_usage"].notna().sum()), "labels": LABELS, "lags": H.LAGS,
                 "max_lead": H.MAX_LEAD, "alpha": H.ALPHA, "break_days": H.BREAK_DAYS,
                 "mature_from": None if ms is None else ms.strftime("%Y-%m-%d"),
                 "mature_threshold_usd": H.MATURE_THRESHOLD_USD},
        "charts": charts, "results": res,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, separators=(",", ":"), allow_nan=False, default=str))
    _report(out)
    return out


def _row(name, r):
    return f"| {name} | {r.get('p')} | {r.get('oos_ratio')} | {r.get('n')} |"


def _report(o: dict) -> None:
    m, r = o["meta"], o["results"]
    q, q3 = r["q12"], r["q3"]
    L = ["# Results - three questions", "",
         f"_Generated by `python run.py` on {m['built_at']}; weeks {m['start']} to {m['as_of']} "
         f"({m['weeks']} weeks with an Adoption Index). Usage source: {m['usage_source']}. "
         f"Adoption Index components: {', '.join(m['adoption_components'])}. Do not edit by hand._", "",
         "| Question | Answer |", "|---|---|",
         f"| Q1. Does Intents volume predict future network adoption? | **{r['answers']['Q1']}** |",
         f"| Q2. Is Intents volume a better predictor than NEAR's price? | **{r['answers']['Q2']}** |",
         f"| Q3. Does Intents activity translate into economically valuable activity for NEAR? | **{r['answers']['Q3']}** |", "",
         "## Q1 and Q2: predicting next week's Adoption Index", "",
         "p = F-test that 2 weekly lags of the predictor add nothing (controls: own lags, BTC lags, break dummy). "
         "OOS = out-of-sample RMSE with / without the predictor (< 1 = it helps).", "",
         "| Model | p | OOS ratio | Weeks |", "|---|---:|---:|---:|",
         _row("Intents volume alone", q["intents_alone"]), _row("NEAR price alone", q["price_alone"]),
         _row("Intents, given price is already in the model", q["intents_beyond_price"]),
         _row("Price, given Intents is already in the model", q["price_beyond_intents"]), "",
         "Lead-lag correlations (weekly growth; k = weeks ahead; bold = p < 0.05):", "",
         "| Predictor | " + " | ".join(f"k={i}" for i in range(m["max_lead"] + 1)) + " |",
         "|---|" + "---:|" * (m["max_lead"] + 1)]
    for x, ll in q["lead_lag"].items():
        L.append(f"| {m['labels'].get(x, x)} | " + " | ".join(
            "n/a" if c["r"] is None else (f"**{c['r']}**" if c["p"] < 0.05 else str(c["r"])) for c in ll) + " |")
    L += ["", "### Robustness (same tests, other measures)", "", "| Target ~ Intents measure | Q1 | Q2 | Intents p | Intents OOS | Price p | Price OOS |",
          "|---|---|---|---:|---:|---:|---:|"]
    for k, v in r["q12_robustness"].items():
        L.append(f"| {k} | {v['q1']} | {v['q2']} | {v['intents_alone']['p']} | {v['intents_alone']['oos_ratio']} | "
                 f"{v['price_alone']['p']} | {v['price_alone']['oos_ratio']} |")
    L += ["", "## Q3: does Intents activity turn into fees for NEAR?", "",
          f"- Same-week elasticity of fees (in NEAR) to Intents volume, BTC-controlled: **{q3.get('elasticity')}** "
          f"(95% CI {q3.get('elasticity_ci')}, p = {q3.get('elasticity_p')}, {q3.get('n')} weeks).",
          f"- Same in USD: {r['q3_usd'].get('elasticity')} (p = {r['q3_usd'].get('elasticity_p')}).",
          f"- Do Intents lags predict fees? p = {q3['predictive'].get('p')}, OOS ratio = {q3['predictive'].get('oos_ratio')}.",
          f"- NEAR fees per $1M of Intents volume: ${q3.get('capture_first_q')} in {q3.get('capture_first_q_label')} -> "
          f"${q3.get('capture_last_q')} in {q3.get('capture_last_q_label')} ({(q3.get('capture_change') or 0):+.1%}).", "",
          "## Data availability", ""]
    if not m["bq_available"]:
        L.append("- BigQuery: **not computed** (no credentials at build time). Usage comes from NearBlocks; contract usage is not in the Adoption Index.")
    else:
        L.append(f"- BigQuery data ends {m.get('bq_last_day')} (freshness check: {m.get('bq_freshness')}); used for the current window: {m['bq_fresh']}.")
    L.append(f"- Explorer API sample: {m.get('sampled_hours', 0)} sampled hours.")
    REPORT.write_text("\n".join(L) + "\n")
