"""NEAR on its own: is it undervalued, fairly valued or overvalued?

Three independent checks, none of which needs another chain:

1. Fair value from NEAR's own multiples. For each fundamental (revenue, DEX
   volume, TVL, stablecoins, returning accounts) ask: "what would NEAR's market
   cap be if it traded at its median multiple of the trailing 2 years?" Fair
   value is the geometric mean across the five; the band uses the 25th-75th
   percentile multiples. Market cap above the band = overvalued.
2. Confidence Premium (Valuation Index - Fundamentals Index), from build.py.
3. Multiples vs their own history: the median percentile of today's five
   multiples within the trailing 2 years (0 = cheapest, 100 = richest).

The verdict is the majority view of the three checks. All windows are
trailing-only (no look-ahead).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

FV_WINDOW = 730
FV_MIN = 365

# multiple name -> (denominator column, is_flow)
ANCHORS = {
    "mc_to_revenue": ("revenue_usd", True),
    "mc_to_dex_volume": ("dex_volume_usd", True),
    "mc_to_tvl": ("tvl_usd", False),
    "mc_to_stablecoins": ("stablecoins_usd", False),
    "mc_to_returning_accounts": ("returning_accounts", False),
}
ANCHOR_LABELS = {
    "mc_to_revenue": "Market cap / revenue (fees burned, annualised)",
    "mc_to_dex_volume": "Market cap / DEX volume (annualised)",
    "mc_to_tvl": "Market cap / TVL",
    "mc_to_stablecoins": "Market cap / stablecoin supply",
    "mc_to_returning_accounts": "Market cap per returning account",
}

PREMIUM_BAND = 15.0      # |premium| beyond this = over/under
MULTIPLE_BAND = (25.0, 75.0)


def denominators(df: pd.DataFrame) -> pd.DataFrame:
    """30-day averages; flows annualised. Shared with the peer comparison."""
    out = {}
    for m, (col, flow) in ANCHORS.items():
        if col in df:
            out[m] = df[col].rolling(30, min_periods=20).mean() * (365 if flow else 1)
    return pd.DataFrame(out, index=df.index)


def multiples(df: pd.DataFrame) -> pd.DataFrame:
    den = denominators(df)
    return den.rdiv(df["market_cap_usd"], axis=0).where(den > 0)


def _rolling_q(s: pd.Series, q: float) -> pd.Series:
    return s.rolling(FV_WINDOW, min_periods=FV_MIN).quantile(q)


def fair_value(df: pd.DataFrame) -> pd.DataFrame:
    den = denominators(df)
    mult = multiples(df)
    logs = {"mid": [], "low": [], "high": []}
    per_anchor = {}
    for m in mult:
        lm = np.log(mult[m])
        for key, q in (("mid", 0.5), ("low", 0.25), ("high", 0.75)):
            fv = np.log(den[m]) + _rolling_q(lm, q)
            logs[key].append(fv)
            if key == "mid":
                per_anchor[m] = np.exp(fv)
    out = pd.DataFrame(index=df.index)
    for key in logs:
        stacked = pd.concat(logs[key], axis=1)
        enough = stacked.notna().sum(axis=1) >= 3   # need at least 3 of 5 anchors
        out[f"fair_value_{key}"] = np.exp(stacked.mean(axis=1)).where(enough)
    out["market_cap_usd"] = df["market_cap_usd"]
    out["fair_value_gap"] = df["market_cap_usd"] / out["fair_value_mid"] - 1
    for m, s in per_anchor.items():
        out[f"fv_{m}"] = s
    return out


def multiple_percentiles(df: pd.DataFrame) -> pd.DataFrame:
    from pipeline.build import rolling_pct
    mult = multiples(df)
    pct = pd.DataFrame({m: rolling_pct(np.log(mult[m]), FV_WINDOW, FV_MIN) for m in mult}, index=df.index)
    pct["median"] = pct.median(axis=1, skipna=True).where(pct.notna().sum(axis=1) >= 3)
    return pct


def _signal(v, lo, hi):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "n/a"
    return "overvalued" if v >= hi else ("undervalued" if v <= lo else "fair")


def verdict_row(fv_row: pd.Series, premium: float, mult_pct: float) -> dict:
    mc, lo, hi = fv_row["market_cap_usd"], fv_row["fair_value_low"], fv_row["fair_value_high"]
    if any(pd.isna(x) for x in (mc, lo, hi)):
        fv_sig = "n/a"
    else:
        fv_sig = "overvalued" if mc > hi else ("undervalued" if mc < lo else "fair")
    sigs = {
        "fair_value": fv_sig,
        "confidence_premium": _signal(premium, -PREMIUM_BAND, PREMIUM_BAND),
        "multiples_vs_history": _signal(mult_pct, *MULTIPLE_BAND),
    }
    votes = list(sigs.values())
    if votes.count("overvalued") >= 2:
        v = "Overvalued"
    elif votes.count("undervalued") >= 2:
        v = "Undervalued"
    elif votes.count("fair") >= 2:
        v = "Fairly valued"
    else:
        v = "Mixed"
    return {"verdict": v, "signals": sigs}


def verdict_series(fv: pd.DataFrame, premium: pd.Series, mpct: pd.Series) -> pd.Series:
    out = {}
    for d in fv.index:
        r = verdict_row(fv.loc[d], premium.get(d, np.nan), mpct.get(d, np.nan))
        if "n/a" in r["signals"].values():
            out[d] = None
        else:
            out[d] = r["verdict"]
    return pd.Series(out)


def fv_backtest(fv: pd.DataFrame, price: pd.Series, horizon: int = 90) -> list[dict]:
    pos = np.where(fv["market_cap_usd"] > fv["fair_value_high"], "above band",
                   np.where(fv["market_cap_usd"] < fv["fair_value_low"], "below band", "inside band"))
    d = pd.DataFrame({"b": pos, "ok": fv["fair_value_mid"].notna(),
                      "f": price.shift(-horizon) / price - 1}, index=fv.index)
    d = d[d.ok].dropna(subset=["f"])
    rows = []
    for lab in ("below band", "inside band", "above band"):
        f = d.f[d.b == lab]
        rows.append({"bucket": f"market cap {lab}", "days": int(len(f)),
                     "median": None if f.empty else round(float(f.median()), 4),
                     "mean": None if f.empty else round(float(f.mean()), 4),
                     "hit_rate": None if f.empty else round(float((f > 0).mean()), 3)})
    return rows


def near_standalone(df: pd.DataFrame, premium: pd.Series) -> dict:
    fv = fair_value(df)
    mpct = multiple_percentiles(df)
    end = fv["fair_value_mid"].dropna().index.max()
    end = min(end, premium.dropna().index.max())
    row = verdict_row(fv.loc[end], float(premium.loc[end]), float(mpct.loc[end, "median"]))
    mult = multiples(df)
    hist = mult.loc[end - pd.Timedelta(days=FV_WINDOW - 1): end]
    table = []
    for m in ANCHORS:
        if m not in mult:
            continue
        table.append({
            "key": m, "label": ANCHOR_LABELS[m],
            "today": float(mult.loc[end, m]) if pd.notna(mult.loc[end, m]) else None,
            "median_2y": float(hist[m].median()) if hist[m].notna().any() else None,
            "percentile_2y": None if pd.isna(mpct.loc[end, m]) else round(float(mpct.loc[end, m]), 1),
            "fair_value": float(fv.loc[end, f"fv_{m}"]) if pd.notna(fv.loc[end, f"fv_{m}"]) else None,
        })
    return {
        "as_of": end.strftime("%Y-%m-%d"),
        "verdict": row["verdict"],
        "signals": row["signals"],
        "market_cap_usd": float(fv.loc[end, "market_cap_usd"]),
        "fair_value_mid": float(fv.loc[end, "fair_value_mid"]),
        "fair_value_low": float(fv.loc[end, "fair_value_low"]),
        "fair_value_high": float(fv.loc[end, "fair_value_high"]),
        "fair_value_gap": float(fv.loc[end, "fair_value_gap"]),
        "premium": float(premium.loc[end]),
        "multiples_percentile": float(mpct.loc[end, "median"]),
        "multiples": table,
        "price_usd": float(df.loc[end, "price_usd"]),
        "implied_price_mid": float(df.loc[end, "price_usd"] * fv.loc[end, "fair_value_mid"] / fv.loc[end, "market_cap_usd"]),
        "_fv": fv, "_mpct": mpct,
    }
