"""Turn data/raw/*.csv into per-chain daily panels, the three pillar scores,
the Fundamentals Index, the Valuation Index and the Confidence Premium.

Everything here is deterministic given data/raw/, so `python run.py --offline`
reproduces the committed outputs byte for byte (sensitivity draws use a fixed seed).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
DOCS_DATA = ROOT / "docs" / "data"
REPORTS = ROOT / "reports"

DISPLAY_DAYS = 730          # what the dashboard shows (2-year lookback)
WINDOW = 365                # trailing window for percentile scores
MIN_PERIODS = 180           # a score needs at least this much history
SMOOTH = 7                  # days, rolling mean before scoring
SEED = 20261114

# metric -> (pillar, higher_is_better, log_transform)
METRICS: dict[str, tuple[str, bool, bool]] = {
    "active_accounts":    ("network", True, True),
    "returning_accounts": ("network", True, True),
    "txns":               ("network", True, True),
    "fees_usd":           ("network", True, True),
    "tvl_usd":            ("defi", True, True),
    "dex_volume_usd":     ("defi", True, True),
    "stablecoins_usd":    ("defi", True, True),
    "staking_ratio":      ("tokenomics", True, False),
    "net_issuance_ann":   ("tokenomics", False, False),
    "burn_offset":        ("tokenomics", True, False),
}
PILLARS = ["network", "defi", "tokenomics"]

LABELS = {
    "active_accounts": "Active accounts (daily signers)",
    "returning_accounts": "Returning accounts (active - new)",
    "retention_ratio": "Returning share of active accounts",
    "txns": "Transactions",
    "fees_usd": "Fees paid (USD)",
    "revenue_usd": "Protocol revenue = fees burned (USD)",
    "tvl_usd": "DeFi TVL (USD)",
    "dex_volume_usd": "DEX volume (USD)",
    "stablecoins_usd": "Stablecoin supply (USD)",
    "staking_ratio": "Staked share of circulating supply",
    "net_issuance_ann": "Net supply growth, annualised (30d)",
    "burn_offset": "Share of gross issuance offset by burn (30d)",
    "market_cap_usd": "Market cap (USD)",
    "price_usd": "Price (USD)",
}


# ------------------------------------------------------------- panels ----
def _read(name: str) -> pd.DataFrame:
    return pd.read_csv(RAW / f"{name}.csv", parse_dates=["date"], index_col="date")


def _complete_days(df: pd.DataFrame) -> pd.DataFrame:
    """Drop today's partial UTC day."""
    today = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize()
    return df[df.index < today]


def _issuance(supply: pd.Series, burn_native: pd.Series) -> tuple[pd.Series, pd.Series]:
    s30 = supply.shift(30)
    net = (supply / s30) ** (365 / 30) - 1
    net_30 = supply - s30
    burn_30 = burn_native.rolling(30, min_periods=25).sum()
    gross = net_30 + burn_30
    offset = (burn_30 / gross).where(gross > 0)
    return net, offset.clip(0, 1)


def near_panel() -> pd.DataFrame:
    nb, ll = _read("near_nearblocks"), _read("near_llama")
    df = nb.join(ll, how="outer")
    df["returning_accounts"] = (df["active_accounts"] - df["new_accounts"]).clip(lower=0)
    df["burn_native"] = df["revenue_usd"] / df["price_usd"]  # 70% of fees are burned on NEAR
    df["net_issuance_ann"], df["burn_offset"] = _issuance(df["total_supply"], df["burn_native"])
    df["fdv_usd"] = df["price_usd"] * df["total_supply"]

    snaps = pd.read_csv(RAW / "near_staking_snapshots.csv", parse_dates=["date"], index_col="date")
    df = df.join(snaps["staked"], how="left")
    df["staking_ratio"] = df["staked"] / df["circulating_supply"]
    df["supply_estimated"] = False
    return _finish(df)


def avax_panel() -> pd.DataFrame:
    ch, mk, ll = _read("avax_chain"), _read("avax_market"), _read("avax_llama")
    df = ch.join(mk, how="outer").join(ll, how="outer")
    # Daily signers on the C-chain are the closest match to NEAR's active-account count.
    df["active_accounts_all"] = df["active_accounts"]
    df["active_accounts"] = df["active_senders"]
    df["returning_accounts"] = (df["active_accounts"] - df["new_accounts"]).clip(lower=0)

    # Circulating supply: CoinGecko only serves 365 days keylessly. Before that,
    # extrapolate the first 90 observed days linearly and flag it; supply-based
    # tokenomics metrics are left empty in the estimated stretch.
    circ = df["circulating_supply_cg"]
    obs = circ.dropna()
    est = pd.Series(False, index=df.index)
    if len(obs) > 30:
        head = obs.iloc[:90]
        x = (head.index - head.index[0]).days.values
        slope, icpt = np.polyfit(x, head.values, 1)
        missing = df.index < obs.index[0]
        xs = (df.index[missing] - head.index[0]).days.values
        circ = circ.copy()
        circ[missing] = icpt + slope * xs
        est[missing] = True
    df["circulating_supply"] = circ.ffill()
    df["supply_estimated"] = est
    df["market_cap_usd"] = df["price_usd"] * df["circulating_supply"]
    df["fdv_usd"] = df["price_usd"] * df["total_supply_snapshot"]

    df["burn_native"] = df["fees_native"]  # all C-chain fees are burned
    net, off = _issuance(df["circulating_supply_cg"], df["burn_native"])
    df["net_issuance_ann"], df["burn_offset"] = net, off
    df["staking_ratio"] = df["staked"].ffill(limit=120) / df["circulating_supply"]
    df.loc[est, "staking_ratio"] = np.nan
    return _finish(df)


def _finish(df: pd.DataFrame) -> pd.DataFrame:
    df = _complete_days(df.sort_index())
    df = df[~df.index.duplicated(keep="last")]
    df["retention_ratio"] = df["returning_accounts"] / df["active_accounts"]
    # Llama's latest day is often not yet published; carry slow stocks, never flows.
    for c in ["tvl_usd", "stablecoins_usd"]:
        df[c] = df[c].ffill(limit=3)
    return df


# ------------------------------------------------------------ scoring ----
def rolling_pct(s: pd.Series, window: int = WINDOW, min_periods: int = MIN_PERIODS) -> pd.Series:
    """Percentile (0-100) of today's value within the trailing `window` days.
    Uses only past and present data - no look-ahead."""
    def f(w):
        last = w[-1]
        if np.isnan(last):
            return np.nan
        w = w[~np.isnan(w)]
        if len(w) < min_periods:
            return np.nan
        return 100.0 * ((w < last).sum() + 0.5 * ((w == last).sum() - 1)) / (len(w) - 1)

    return s.rolling(window, min_periods=1).apply(f, raw=True)


def metric_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = {}
    for m, (_, higher, log) in METRICS.items():
        if m not in df or df[m].notna().sum() < MIN_PERIODS:
            continue
        x = df[m].astype(float)
        if log:
            x = np.log(x.where(x > 0))
        x = x.rolling(SMOOTH, min_periods=4).mean()
        sc = rolling_pct(x)
        out[m] = sc if higher else 100 - sc
    return pd.DataFrame(out, index=df.index)


def combine(scores: pd.DataFrame, pillar_w=None, metric_w=None) -> pd.DataFrame:
    pillar_w = pillar_w or {p: 1.0 for p in PILLARS}
    res = {}
    for p in PILLARS:
        cols = [m for m in scores if METRICS[m][0] == p]
        if not cols:
            continue
        w = np.array([(metric_w or {}).get(m, 1.0) for m in cols])
        v = scores[cols].values
        mask = ~np.isnan(v)
        num = np.nansum(v * w, axis=1)
        den = (mask * w).sum(axis=1)
        res[p] = pd.Series(np.where(den > 0, num / np.where(den > 0, den, 1), np.nan), index=scores.index)
    pil = pd.DataFrame(res)
    pw = np.array([pillar_w.get(p, 1.0) for p in pil.columns])
    v = pil.values
    mask = ~np.isnan(v)
    den = (mask * pw).sum(axis=1)
    fund = np.where(den > 0, np.nansum(v * pw, axis=1) / np.where(den > 0, den, 1), np.nan)
    pil["fundamentals"] = fund
    return pil


def valuation_score(df: pd.DataFrame) -> pd.Series:
    x = np.log(df["market_cap_usd"].where(df["market_cap_usd"] > 0)).rolling(SMOOTH, min_periods=4).mean()
    return rolling_pct(x)


def sensitivity(scores: dict[str, pd.DataFrame], val: dict[str, pd.Series], n: int = 2000) -> dict:
    rng = np.random.default_rng(SEED)
    res = {c: [] for c in scores}
    res["near_minus_avax"] = []
    last = {c: scores[c].dropna(how="all").index.max() for c in scores}
    for _ in range(n):
        pw = dict(zip(PILLARS, rng.dirichlet(np.ones(len(PILLARS)))))
        mw = {m: float(rng.uniform(0.25, 1.75)) for m in METRICS}
        prem = {}
        for c, sc in scores.items():
            d = last[c]
            f = combine(sc.loc[[d]], pw, mw)["fundamentals"].iloc[0]
            prem[c] = float(val[c].loc[d] - f)
            res[c].append(prem[c])
        res["near_minus_avax"].append(prem["near"] - prem["avax"])
    out = {}
    for k, v in res.items():
        a = np.array(v)
        out[k] = {
            "median": round(float(np.median(a)), 1),
            "p05": round(float(np.percentile(a, 5)), 1),
            "p95": round(float(np.percentile(a, 95)), 1),
            "share_negative": round(float((a < 0).mean()), 3),
        }
    out["draws"] = n
    return out


# ------------------------------------------------------------- ratios ----
def snapshot(df: pd.DataFrame) -> dict:
    """Trailing-30-day fundamentals and valuation multiples at the latest date."""
    d = df.dropna(subset=["market_cap_usd"]).index.max()
    w = df.loc[d - pd.Timedelta(days=29): d]
    y = df.loc[d - pd.Timedelta(days=365 + 29): d - pd.Timedelta(days=365)]
    ann = lambda c: w[c].mean() * 365
    mc = df.loc[d, "market_cap_usd"]
    fdv = df.loc[d, "fdv_usd"]
    tvl = w["tvl_usd"].dropna().iloc[-1]
    stables = w["stablecoins_usd"].dropna().iloc[-1]
    act = w["active_accounts"].mean()
    s = {
        "as_of": d.strftime("%Y-%m-%d"),
        "price_usd": df.loc[d, "price_usd"],
        "market_cap_usd": mc,
        "fdv_usd": fdv,
        "fees_ann_usd": ann("fees_usd"),
        "revenue_ann_usd": ann("revenue_usd"),
        "tvl_usd": tvl,
        "dex_volume_ann_usd": ann("dex_volume_usd"),
        "stablecoins_usd": stables,
        "active_accounts_30d": act,
        "retention_ratio_30d": w["retention_ratio"].mean(),
        "txns_30d_avg": w["txns"].mean(),
        "staking_ratio": df["staking_ratio"].dropna().iloc[-1] if df["staking_ratio"].notna().any() else None,
        "net_issuance_ann": df["net_issuance_ann"].dropna().iloc[-1] if df["net_issuance_ann"].notna().any() else None,
        "net_issuance_365d": None,
        "burn_offset_30d": df["burn_offset"].dropna().iloc[-1] if df["burn_offset"].notna().any() else None,
    }
    supply_col = "total_supply" if "total_supply" in df else "circulating_supply_cg"
    sup = df[supply_col].dropna()
    if len(sup) and sup.index[0] <= d - pd.Timedelta(days=365):
        s["net_issuance_365d"] = sup.iloc[-1] / sup.loc[: d - pd.Timedelta(days=365)].iloc[-1] - 1
    s["mc_to_fees"] = mc / s["fees_ann_usd"]
    s["mc_to_revenue"] = mc / s["revenue_ann_usd"]
    s["mc_to_tvl"] = mc / tvl
    s["fdv_to_tvl"] = fdv / tvl
    s["mc_to_dex_volume"] = mc / s["dex_volume_ann_usd"]
    s["mc_to_stablecoins"] = mc / stables
    s["mc_per_active_account"] = mc / act
    s["revenue_per_active_account"] = s["revenue_ann_usd"] / act
    for c in ["active_accounts", "txns", "fees_usd", "revenue_usd", "tvl_usd", "dex_volume_usd", "stablecoins_usd", "market_cap_usd"]:
        prev = y[c].mean() if len(y) else np.nan
        s[f"yoy_{c}"] = w[c].mean() / prev - 1 if prev and not np.isnan(prev) else None
    return {k: (None if v is None or (isinstance(v, float) and not np.isfinite(v)) else (float(v) if not isinstance(v, str) else v)) for k, v in s.items()}


def relative_series(near: pd.DataFrame, avax: pd.DataFrame) -> pd.DataFrame:
    """NEAR multiple divided by AVAX multiple (>1 = NEAR priced richer per unit)."""
    def mult(df, num, den, flow):
        d = df[den].rolling(30, min_periods=20).mean() * (365 if flow else 1)
        return df[num] / d
    idx = near.index.intersection(avax.index)
    out = pd.DataFrame(index=idx)
    for name, den, flow in [("mc_to_revenue", "revenue_usd", True), ("mc_to_tvl", "tvl_usd", False),
                            ("mc_to_dex_volume", "dex_volume_usd", True), ("mc_to_active", "active_accounts", False)]:
        out[name] = (mult(near, "market_cap_usd", den, flow) / mult(avax, "market_cap_usd", den, flow)).loc[idx]
    return out


def backtest(df: pd.DataFrame, horizon: int = 90) -> list[dict]:
    """Forward price return after each Confidence Premium bucket. Descriptive
    only: overlapping windows, small sample, one market regime."""
    d = pd.DataFrame({"p": df["confidence_premium"], "f": df["price_usd"].shift(-horizon) / df["price_usd"] - 1}).dropna()
    rows = []
    for lab, m in [("premium <= -15", d.p <= -15), ("-15 < premium < +15", (d.p > -15) & (d.p < 15)), ("premium >= +15", d.p >= 15)]:
        f = d.f[m]
        rows.append({"bucket": lab, "days": int(m.sum()),
                     "median": None if f.empty else round(float(f.median()), 4),
                     "mean": None if f.empty else round(float(f.mean()), 4),
                     "hit_rate": None if f.empty else round(float((f > 0).mean()), 3)})
    return rows


# -------------------------------------------------------------- build ----
def _round(x, nd=2):
    return [None if (v is None or not np.isfinite(v)) else round(float(v), nd) for v in x]


def build() -> dict:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    DOCS_DATA.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    panels = {"near": near_panel(), "avax": avax_panel()}
    scores, vals, indices = {}, {}, {}
    for c, df in panels.items():
        sc = metric_scores(df)
        idx = combine(sc)
        v = valuation_score(df)
        idx["valuation"] = v
        idx["confidence_premium"] = v - idx["fundamentals"]
        scores[c], vals[c], indices[c] = sc, v, idx
        df.join(sc.add_prefix("score_")).join(idx).to_csv(PROCESSED / f"{c}_daily.csv", float_format="%.6g")

    rel = relative_series(panels["near"], panels["avax"])
    rel.to_csv(PROCESSED / "relative_near_vs_avax.csv", float_format="%.6g")
    snaps = {c: snapshot(df) for c, df in panels.items()}
    sens = sensitivity(scores, vals)
    bt = {c: backtest(panels[c].join(indices[c][["confidence_premium"]])) for c in panels}

    end = min(indices["near"]["fundamentals"].dropna().index.max(), indices["avax"]["fundamentals"].dropna().index.max())
    start = end - pd.Timedelta(days=DISPLAY_DAYS - 1)
    dates = pd.date_range(start, end, freq="D")

    series = {}
    for c in panels:
        df = panels[c].reindex(dates)
        idx = indices[c].reindex(dates)
        sc = scores[c].reindex(dates)
        smooth = lambda col: df[col].rolling(SMOOTH, min_periods=4).mean() if col in df else pd.Series(np.nan, index=dates)
        series[c] = {
            "index": {k: _round(idx[k], 1) for k in idx.columns},
            "scores": {k: _round(sc[k], 1) for k in sc.columns},
            "metrics": {
                k: _round(smooth(k), 4) for k in
                ["active_accounts", "returning_accounts", "retention_ratio", "txns", "fees_usd", "revenue_usd", "tvl_usd",
                 "dex_volume_usd", "stablecoins_usd", "staking_ratio", "net_issuance_ann", "burn_offset",
                 "market_cap_usd", "price_usd"]
            },
        }
    relw = rel.reindex(dates)
    latest = {c: {k: (None if pd.isna(v) else round(float(v), 1)) for k, v in indices[c].loc[end].items()} for c in panels}

    out = {
        "meta": {
            "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "fetched_at": (RAW / "FETCHED_AT").read_text().strip() if (RAW / "FETCHED_AT").exists() else None,
            "as_of": end.strftime("%Y-%m-%d"),
            "window_days": WINDOW, "smooth_days": SMOOTH, "display_days": DISPLAY_DAYS,
            "metrics": {m: {"pillar": p, "higher_is_better": h, "label": LABELS[m]} for m, (p, h, _) in METRICS.items()},
            "labels": LABELS,
            "near_staking_snapshots": int(panels["near"]["staked"].notna().sum()),
        },
        "dates": [d.strftime("%Y-%m-%d") for d in dates],
        "series": series,
        "relative": {k: _round(relw[k], 3) for k in relw.columns},
        "latest": latest,
        "snapshot": snaps,
        "sensitivity": sens,
        "backtest": {"horizon_days": 90, "rows": bt},
    }
    (DOCS_DATA / "dashboard.json").write_text(json.dumps(out, separators=(",", ":"), allow_nan=False))
    from pipeline.report import write_report
    write_report(out, REPORTS / "latest.md")
    return out
