"""Test: "Cross-chain volume through NEAR Intents is a better leading indicator
of real network usage than token price."

Everything is weekly (Mon-Sun, complete weeks only) and in log growth
(week-on-week change of log level), so shared long-run trends cannot create
a fake relationship.

Predictors   intents_usd     NEAR Intents USD volume (DefiLlama, complete)
             intents_swaps   successful 1Click swaps (Explorer API, sampled hours)
             near_price      NEAR price (NearBlocks)
Control      btc_price       BTC price: market-wide moves
Targets      network-usage series from BigQuery (or NearBlocks where BigQuery
             is unavailable/stale - the source is always labelled)

Tests, decided before looking at results:
 1. Lead-lag correlation, lags 0-8 weeks: corr(x_t, y_{t+k}).
 2. In-sample predictive test: y_t on 2 own lags + 2 BTC lags, adding 2 lags
    of the predictor; F-test that the predictor lags are all zero.
 3. Out-of-sample: expanding window from the middle of the sample, one-week-
    ahead forecasts; RMSE relative to the baseline (own lags + BTC). < 1 = helps.

Verdict rule (per target): Intents "beats" price when the best Intents measure
has p < 0.05 in test 2 AND an out-of-sample RMSE ratio below 1 AND below
price's ratio. The hypothesis is SUPPORTED if Intents beats price on most
targets, REJECTED if price does at least as well on most targets (or Intents
never passes test 2 while price sometimes does), NOT SUPPORTED if neither
passes, MIXED otherwise.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

LAGS = 2
MAX_LEAD = 8
ALPHA = 0.05
PREDICTORS = {
    "intents_usd": "NEAR Intents volume (USD)",
    "intents_swaps": "NEAR Intents swap count (sampled)",
    "near_price": "NEAR price",
}
CONTROL = "btc_price"


def weekly(daily: pd.DataFrame, how: dict[str, str]) -> pd.DataFrame:
    d = daily.copy()
    out = {}
    for c, agg in how.items():
        if c not in d:
            continue
        r = d[c].resample("W-SUN")
        s = r.sum(min_count=6) if agg == "sum" else r.mean()
        n = r.count()
        out[c] = s.where(n >= 6)  # need at least 6 of 7 days
    w = pd.DataFrame(out)
    today = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize()
    return w[w.index < today]  # drop the current, incomplete week


def growth(w: pd.DataFrame) -> pd.DataFrame:
    return np.log(w.where(w > 0)).diff()


def lead_lag(x: pd.Series, y: pd.Series) -> list[dict]:
    rows = []
    for k in range(0, MAX_LEAD + 1):
        d = pd.DataFrame({"x": x, "y": y.shift(-k)}).dropna()
        if len(d) < 20:
            rows.append({"lag": k, "r": None, "p": None, "n": len(d)})
            continue
        r, p = stats.pearsonr(d.x, d.y)
        rows.append({"lag": k, "r": round(float(r), 3), "p": round(float(p), 4), "n": len(d)})
    return rows


def _design(df: pd.DataFrame, y: str, xs: list[str]) -> pd.DataFrame:
    cols = {"y": df[y]}
    for v in [y] + xs:
        for l in range(1, LAGS + 1):
            cols[f"{v}_l{l}"] = df[v].shift(l)
    return pd.DataFrame(cols).dropna()


def predictive(df: pd.DataFrame, y: str, x: str) -> dict:
    base_x = [CONTROL] if CONTROL in df else []
    d = _design(df, y, base_x + [x])
    if len(d) < 30:
        return {"n": len(d), "p": None, "oos_ratio": None}
    X = sm.add_constant(d.drop(columns="y"))
    fit = sm.OLS(d["y"], X).fit()
    hyp = " = 0, ".join(f"{x}_l{l}" for l in range(1, LAGS + 1)) + " = 0"
    p = float(fit.f_test(hyp).pvalue)

    # out-of-sample, expanding window from the middle of the sample
    base_cols = [c for c in X.columns if not c.startswith(f"{x}_l")]
    start = len(d) // 2
    e_full, e_base = [], []
    for t in range(start, len(d)):
        tr, te = slice(0, t), slice(t, t + 1)
        f1 = sm.OLS(d["y"].iloc[tr], X.iloc[tr]).fit()
        f0 = sm.OLS(d["y"].iloc[tr], X[base_cols].iloc[tr]).fit()
        e_full.append(float(d["y"].iloc[te].values[0] - f1.predict(X.iloc[te]).values[0]))
        e_base.append(float(d["y"].iloc[te].values[0] - f0.predict(X[base_cols].iloc[te]).values[0]))
    rmse = lambda e: float(np.sqrt(np.mean(np.square(e))))
    return {"n": len(d), "n_oos": len(e_full), "p": round(p, 4),
            "oos_ratio": round(rmse(e_full) / rmse(e_base), 3),
            "first_week": d.index[0].strftime("%Y-%m-%d"), "last_week": d.index[-1].strftime("%Y-%m-%d")}


def run(w: pd.DataFrame, targets: dict[str, str]) -> dict:
    g = growth(w)
    results, verdicts = {}, {}
    for t, label in targets.items():
        if t not in g or g[t].notna().sum() < 30:
            continue
        res = {}
        for x in PREDICTORS:
            if x not in g or g[x].notna().sum() < 30:
                continue
            res[x] = {"lead_lag": lead_lag(g[x], g[t]), **predictive(g, t, x)}
        results[t] = res
        verdicts[t] = _verdict(res)
    tally = pd.Series([v["winner"] for v in verdicts.values()]).value_counts().to_dict()
    n = len(verdicts)
    intents_wins = tally.get("intents", 0)
    price_wins = tally.get("price", 0)
    any_intents_sig = any(v["intents_significant"] for v in verdicts.values())
    if n and intents_wins > n / 2:
        overall = "SUPPORTED"
    elif n and price_wins >= n / 2:
        overall = "REJECTED"            # price leads usage at least as well
    elif n and not any_intents_sig and price_wins == 0:
        overall = "NOT SUPPORTED"       # neither Intents nor price leads usage
    elif n and not any_intents_sig:
        overall = "REJECTED"
    else:
        overall = "MIXED"
    return {"results": results, "verdicts": verdicts, "overall": overall,
            "tally": tally, "n_targets": n}


def _passes(r: dict | None) -> bool:
    return bool(r and r.get("p") is not None and r["p"] < ALPHA and r.get("oos_ratio") is not None and r["oos_ratio"] < 1)


def _verdict(res: dict) -> dict:
    intents = [k for k in ("intents_usd", "intents_swaps") if k in res]
    best_i = min(intents, key=lambda k: (res[k].get("oos_ratio") or 9e9)) if intents else None
    ri, rp = (res.get(best_i) if best_i else None), res.get("near_price")
    i_ok, p_ok = _passes(ri), _passes(rp)
    ir = ri.get("oos_ratio") if ri else None
    pr = rp.get("oos_ratio") if rp else None
    if i_ok and (pr is None or ir < pr):
        winner = "intents"
    elif p_ok and (ir is None or pr <= ir):
        winner = "price"
    elif i_ok or p_ok:
        winner = "intents" if i_ok else "price"
    else:
        winner = "neither"
    return {"best_intents_measure": best_i, "winner": winner,
            "intents_significant": bool(ri and ri.get("p") is not None and ri["p"] < ALPHA),
            "intents_oos_ratio": ir, "price_oos_ratio": pr,
            "intents_p": ri.get("p") if ri else None, "price_p": rp.get("p") if rp else None}
