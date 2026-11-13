"""Optional comparisons. The NEAR verdict never depends on anything here.

Peers
-----
avax       Avalanche C-chain (full panel, built in build.py)
thorchain  business-model peer: a cross-chain swap venue, like NEAR Intents
basket     median of six L1s: Avalanche, Sui, Aptos, TON, ICP, Cardano

Pump.fun event study
--------------------
Pump.fun's app added NEAR ecosystem tokens on 2026-11-04 and Avalanche tokens
shortly after (2026-11-05 is used and flagged approximate: secondary reports
only say the AVAX integration was announced after NEAR's went live). Each
chain's metrics are indexed to their own 14 days before go-live (= 100). The
control group is the median of L1s Pump.fun did not add, aligned to NEAR's date.
This describes what happened after the event; it does not attribute cause.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pipeline.valuation import multiples

BASKET = ["avax", "sui", "aptos", "ton", "icp", "cardano"]
CONTROL = ["sui", "aptos", "ton", "icp", "cardano"]
PEER_LABELS = {"avax": "AVAX (C-chain)", "thorchain": "THORChain", "basket": "L1 basket median"}

PUMPFUN = {
    "near": {"date": "2026-11-04", "approximate": False},
    "avax": {"date": "2026-11-05", "approximate": True},
}
PRE_DAYS = 14
EVENT_METRICS = ["active_accounts", "txns", "fees_usd", "dex_volume_usd"]
GROWTH_COLS = ["tvl_usd", "dex_volume_usd", "fees_usd", "revenue_usd", "stablecoins_usd"]


def peer_panels(raw: pd.DataFrame, avax: pd.DataFrame) -> dict[str, pd.DataFrame]:
    out = {"avax": avax}
    for c, g in raw.groupby("chain"):
        g = g.drop(columns="chain").sort_index()
        g = g[~g.index.duplicated(keep="last")]
        for col in ("tvl_usd", "stablecoins_usd"):
            g[col] = g[col].ffill(limit=3)
        out[c] = g
    return out


def _yoy(s: pd.Series, end: pd.Timestamp):
    s = s.dropna()
    a = s.loc[end - pd.Timedelta(days=29): end]
    b = s.loc[end - pd.Timedelta(days=394): end - pd.Timedelta(days=365)]
    if len(a) < 20 or len(b) < 20 or b.mean() <= 0:
        return None
    return float(a.mean() / b.mean() - 1)


def comparison(near: pd.DataFrame, panels: dict[str, pd.DataFrame], dates: pd.DatetimeIndex) -> dict:
    mults = {c: multiples(df) for c, df in panels.items()}
    mults["near"] = multiples(near)
    names = list(mults["near"].columns)
    # Basket = median of the members' multiples, day by day (members missing a day are skipped).
    basket = {}
    for m in names:
        cols = pd.concat([mults[c][m] for c in BASKET if c in mults and m in mults[c]], axis=1)
        # a basket median needs at least 3 members reporting that day
        basket[m] = cols.median(axis=1, skipna=True).where(cols.notna().sum(axis=1) >= 3)
    mults["basket"] = pd.DataFrame(basket)

    end = dates[-1]
    series, latest, growth = {}, {}, {}
    for key in ["near", "avax", "thorchain", "basket"]:
        M = mults[key].reindex(dates)
        series[key] = {m: [None if pd.isna(v) else round(float(v), 4) for v in M[m]] for m in names if m in M}
        last = mults[key].loc[:end].ffill(limit=3).iloc[-1] if len(mults[key].loc[:end]) else pd.Series(dtype=float)
        latest[key] = {m: (None if pd.isna(last.get(m)) else float(last.get(m))) for m in names}

    for key in ["near", "avax", "thorchain"]:
        df = near if key == "near" else panels[key]
        growth[key] = {c: _yoy(df[c], end) if c in df else None for c in GROWTH_COLS}
    growth["basket"] = {
        c: (lambda xs: float(np.median(xs)) if xs else None)(
            [g for g in (_yoy(panels[b][c], end) for b in BASKET if b in panels and c in panels[b]) if g is not None])
        for c in GROWTH_COLS}

    return {"labels": PEER_LABELS, "multiples": series, "latest": latest, "growth": growth,
            "basket_members": BASKET}


def event_study(near: pd.DataFrame, panels: dict[str, pd.DataFrame]) -> dict:
    out = {"pre_days": PRE_DAYS, "events": PUMPFUN, "series": {}, "post_days": 0}
    last_day = near.index.max()
    for chain, ev in PUMPFUN.items():
        df = near if chain == "near" else panels[chain]
        d0 = pd.Timestamp(ev["date"])
        out["series"][chain] = _indexed(df, d0, EVENT_METRICS)
    # control: same calendar window as NEAR, DefiLlama metrics only
    d0 = pd.Timestamp(PUMPFUN["near"]["date"])
    ctl = {}
    for m in ["fees_usd", "dex_volume_usd"]:
        cols = [_indexed(panels[c], d0, [m])[m] for c in CONTROL if c in panels and m in panels[c]]
        cols = [pd.Series(c) for c in cols if c]
        ctl[m] = [None if pd.isna(v) else round(float(v), 1) for v in pd.concat(cols, axis=1).median(axis=1)] if cols else []
    out["series"]["control"] = ctl
    out["post_days"] = int((last_day - d0).days)
    n = PRE_DAYS + out["post_days"] + 1
    out["days"] = list(range(-PRE_DAYS, -PRE_DAYS + n))
    for k, s in out["series"].items():
        for m in list(s):
            s[m] = (s[m] + [None] * n)[:n]
    # summary: mean index over the post-event days
    out["summary"] = {k: {m: (None if not any(v is not None for v in vals[PRE_DAYS:]) else
                              round(float(np.nanmean([v for v in vals[PRE_DAYS:] if v is not None])) - 100, 1))
                          for m, vals in s.items()} for k, s in out["series"].items()}
    return out


def _indexed(df: pd.DataFrame, d0: pd.Timestamp, cols: list[str]) -> dict[str, list]:
    res = {}
    for m in cols:
        if m not in df:
            continue
        s = df[m]
        base = s.loc[d0 - pd.Timedelta(days=PRE_DAYS): d0 - pd.Timedelta(days=1)].mean()
        win = s.reindex(pd.date_range(d0 - pd.Timedelta(days=PRE_DAYS), s.index.max()))
        res[m] = [None if (pd.isna(v) or not base) else round(float(v / base * 100), 1) for v in win] if base and not pd.isna(base) else []
    return res
