"""Three questions, three variables (+ one for Q3), all weekly.

  X1  NEAR Intents volume         candidate leading indicator
  X2  NEAR token price            competing indicator
  Y   Network Adoption Index      geometric mean of active accounts, transactions
                                  and contract usage, each indexed to 100
  V   Economic value to NEAR      fees burned (in NEAR, and in USD)        - Q3 only
  C   BTC price                   market-wide control in every regression

Primary target (fix 2): Real Usage Index = geometric mean of returning signers
(signed this week and in one of the 4 previous weeks; BigQuery) and fees burned
in NEAR - measures bots cannot cheaply fake. Returning signers join the index only
when BigQuery covers the whole window; until then the index is fees burned alone.
("Active minus new accounts" is NOT used: NearBlocks new accounts can exceed
active signers, so that difference hits zero in some weeks.) The broad
Adoption Index is reported as a secondary target.
Robustness (fix 3): every test is repeated from the first day the 30-day average
Intents volume exceeds $1M/day (before that its growth rates are launch noise).

Q1  Does Intents volume predict future adoption?
Q2  Is Intents volume a better predictor than NEAR's price?
Q3  Does Intents activity translate into economically valuable activity for NEAR?

Method (fixed before looking at results)
* Complete Mon-Sun weeks; every series in weekly log growth, so shared
  long-run trends cannot create a fake relationship.
* One documented break gets an impulse dummy: the week containing 2026-04-02,
  when NEAR transactions fell 72% and fees 62% in a day while active accounts
  barely moved (a large automated sender stopping), and the week after it,
  because a mid-week level shift splits across two weekly averages.
  No other outliers are touched.
* Predictive model: y_t on 2 own lags + 2 BTC lags (+ dummy), then add 2 lags of
  the predictor. F-test (alpha 0.05) that the predictor lags are zero.
  Out-of-sample: expanding window from mid-sample, one-week-ahead RMSE with the
  predictor / without it (< 1 = it helps).

Verdict rules
Q1  YES if Intents passes the F-test AND its out-of-sample ratio < 1;
    PARTLY if only one of the two holds; NO otherwise.
Q2  YES if Intents adds information beyond price (Intents lags significant in a
    model that already has price lags) AND price does not add information beyond
    Intents AND Intents' out-of-sample ratio < price's; NO if price wins those;
    TIE if neither predictor helps; MIXED otherwise.
Q3  YES if fees (in NEAR) rise with Intents volume in the same week (elasticity
    > 0, p < 0.05, BTC-controlled) AND fees per $ of Intents volume did not fall
    by more than half from the first to the last quarter; PARTLY if only the
    elasticity holds; NO if the elasticity is not significant.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

LAGS = 2
MAX_LEAD = 8
ALPHA = 0.05
CONTROL = "btc_price"
BREAK_DAYS = ["2026-04-02"]


def weekly(daily: pd.DataFrame, how: dict[str, str]) -> pd.DataFrame:
    out = {}
    for c, agg in how.items():
        if c not in daily:
            continue
        r = daily[c].resample("W-SUN")
        s = r.sum(min_count=6) if agg == "sum" else r.mean()
        out[c] = s.where(r.count() >= 6)
    w = pd.DataFrame(out)
    today = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize()
    return w[w.index < today - pd.Timedelta(days=0)]


def growth(w: pd.DataFrame) -> pd.DataFrame:
    return np.log(w.where(w > 0)).diff()


def adoption_index(w: pd.DataFrame, comps: list[str]) -> pd.Series:
    """Geometric mean of the components, each indexed to 100 at its first value."""
    idx = [w[c] / w[c].dropna().iloc[0] * 100 for c in comps if c in w and w[c].notna().any()]
    if not idx:
        return pd.Series(dtype=float)
    m = pd.concat(idx, axis=1)
    return np.exp(np.log(m).mean(axis=1)).where(m.notna().all(axis=1))


def break_dummy(index: pd.DatetimeIndex) -> pd.Series:
    """1 for the week containing each break AND the week after: a mid-week level
    shift splits across two weekly averages, so both weeks' growth carries it."""
    d = pd.Series(0.0, index=index)
    for day in BREAK_DAYS:
        wk = pd.Timestamp(day).to_period("W-SUN").end_time.normalize()
        for w in (wk, wk + pd.Timedelta(days=7)):
            if w in d.index:
                d.loc[w] = 1.0
    return d


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


def _design(g: pd.DataFrame, y: str, xs: list[str]) -> pd.DataFrame:
    cols = {"y": g[y]}
    for v in [y] + xs:
        for l in range(1, LAGS + 1):
            cols[f"{v}_l{l}"] = g[v].shift(l)
    cols["break"] = break_dummy(g.index)
    d = pd.DataFrame(cols).dropna()
    if d["break"].sum() == 0:
        d = d.drop(columns="break")
    return d


def _lags(v):
    return [f"{v}_l{l}" for l in range(1, LAGS + 1)]


def predictive(g: pd.DataFrame, y: str, x: str, also: list[str] | None = None) -> dict:
    """F-test and out-of-sample gain of adding x's lags to: own lags + BTC lags (+ `also` lags)."""
    base = [CONTROL] + (also or [])
    d = _design(g, y, base + [x])
    if len(d) < 30:
        return {"n": len(d), "p": None, "oos_ratio": None}
    X = sm.add_constant(d.drop(columns="y"))
    fit = sm.OLS(d["y"], X).fit()
    p = float(fit.f_test(" = 0, ".join(_lags(x)) + " = 0").pvalue)
    base_cols = [c for c in X.columns if c not in _lags(x)]
    start = len(d) // 2
    e1, e0 = [], []
    for t in range(start, len(d)):
        # a column that is all zero in the training window (the break dummy before the break) is dropped
        live = [c for c in X.columns if c == "const" or X[c].iloc[:t].abs().sum() > 0]
        c1, c0 = live, [c for c in live if c in base_cols]
        f1 = sm.OLS(d["y"].iloc[:t], X[c1].iloc[:t]).fit()
        f0 = sm.OLS(d["y"].iloc[:t], X[c0].iloc[:t]).fit()
        yt = d["y"].iloc[t]
        e1.append(yt - float(f1.predict(X[c1].iloc[[t]]).iloc[0]))
        e0.append(yt - float(f0.predict(X[c0].iloc[[t]]).iloc[0]))
    rmse = lambda e: float(np.sqrt(np.mean(np.square(e))))
    coef = float(sum(fit.params[c] for c in _lags(x)))
    return {"n": len(d), "n_oos": len(e1), "p": round(p, 4), "oos_ratio": round(rmse(e1) / rmse(e0), 3),
            "sum_of_lag_coefs": round(coef, 4),
            "first_week": d.index[0].strftime("%Y-%m-%d"), "last_week": d.index[-1].strftime("%Y-%m-%d")}


def _ok(r):
    return r.get("p") is not None and r["p"] < ALPHA


def q1_q2(g: pd.DataFrame, y: str, intents: str, price: str = "near_price") -> dict:
    r_i = predictive(g, y, intents)
    r_p = predictive(g, y, price)
    i_beyond_p = predictive(g, y, intents, also=[price])   # does Intents add info once price is known?
    p_beyond_i = predictive(g, y, price, also=[intents])   # and vice versa
    ll = {intents: lead_lag(g[intents], g[y]), price: lead_lag(g[price], g[y])}

    i_sig, i_oos = _ok(r_i), (r_i.get("oos_ratio") or 9) < 1
    q1 = "YES" if (i_sig and i_oos) else ("PARTLY" if (i_sig or i_oos) else "NO")

    p_sig, p_oos = _ok(r_p), (r_p.get("oos_ratio") or 9) < 1
    if _ok(i_beyond_p) and not _ok(p_beyond_i) and (r_i["oos_ratio"] or 9) < (r_p["oos_ratio"] or 9):
        q2 = "YES"
    elif _ok(p_beyond_i) and not _ok(i_beyond_p) and (r_p["oos_ratio"] or 9) <= (r_i["oos_ratio"] or 9):
        q2 = "NO"
    elif not (i_sig or i_oos or p_sig or p_oos):
        q2 = "TIE (neither predicts)"
    else:
        q2 = "MIXED"
    return {"target": y, "intents": intents, "q1": q1, "q2": q2, "lead_lag": ll,
            "intents_alone": r_i, "price_alone": r_p,
            "intents_beyond_price": i_beyond_p, "price_beyond_intents": p_beyond_i}


def q3(w: pd.DataFrame, intents: str = "intents_usd", value: str = "fees_native",
       value_usd: str = "fees_usd", mature_from: pd.Timestamp | None = None) -> dict:
    g = growth(w)
    d = pd.DataFrame({"v": g[value], "x": g[intents], "c": g[CONTROL], "brk": break_dummy(g.index)}).dropna()
    out = {"value": value, "n": len(d)}
    if len(d) < 30:
        return {**out, "verdict": "NOT COMPUTED"}
    X = sm.add_constant(d[["x", "c"] + (["brk"] if d["brk"].sum() else [])])
    fit = sm.OLS(d["v"], X).fit(cov_type="HC1")
    out["elasticity"] = round(float(fit.params["x"]), 4)
    out["elasticity_p"] = round(float(fit.pvalues["x"]), 4)
    out["elasticity_ci"] = [round(float(v), 4) for v in fit.conf_int().loc["x"]]
    out["predictive"] = predictive(g, value, intents)
    out["lead_lag"] = lead_lag(g[intents], g[value])

    cap = (w[value_usd] / w[intents] * 1e6).replace([np.inf, -np.inf], np.nan).dropna()
    q = cap.resample("QE").mean().dropna()
    out["capture_first_q"] = round(float(q.iloc[0]), 2) if len(q) else None
    out["capture_last_q"] = round(float(q.iloc[-1]), 2) if len(q) else None
    out["capture_first_q_label"] = str(q.index[0].to_period("Q")) if len(q) else None
    out["capture_last_q_label"] = str(q.index[-1].to_period("Q")) if len(q) else None
    out["capture_change"] = round(float(q.iloc[-1] / q.iloc[0] - 1), 4) if len(q) > 1 else None

    # Descriptive, not part of the verdict: quarterly fees per $1M from summed quarters,
    # from the first FULL quarter after Intents passed $1M/day to the last COMPLETE quarter.
    qs = pd.DataFrame({"f": w[value_usd], "i": w[intents]}).dropna().resample("QE").agg(["sum", "count"])
    full = qs[("f", "count")] >= 12                       # complete quarters only (>= 12 weeks)
    per = (qs[("f", "sum")] / qs[("i", "sum")] * 1e6)
    out["capture_quarters"] = {str(k.to_period("Q")): round(float(v), 1) for k, v in per.items() if pd.notna(v)}
    if mature_from is not None:
        start_q = (pd.Timestamp(mature_from).to_period("Q") + 1).end_time.normalize()
        cand = per[(per.index >= start_q) & full]
        if len(cand) >= 2:
            out["capture_post_launch_from"] = str(cand.index[0].to_period("Q"))
            out["capture_post_launch_first"] = round(float(cand.iloc[0]), 1)
            out["capture_post_launch_to"] = str(cand.index[-1].to_period("Q"))
            out["capture_post_launch_last"] = round(float(cand.iloc[-1]), 1)
            out["capture_post_launch_change"] = round(float(cand.iloc[-1] / cand.iloc[0] - 1), 4)

    pos = out["elasticity"] > 0 and out["elasticity_p"] < ALPHA
    held = out["capture_change"] is not None and out["capture_change"] > -0.5
    out["verdict"] = "YES" if (pos and held) else ("PARTLY" if pos else "NO")
    return out


REAL_USAGE = ["returning_signers", "fees_native"]    # hard to fake: repeat users (BigQuery), fees actually paid
MATURE_THRESHOLD_USD = 1e6                          # mature window: 30-day avg Intents volume > $1M/day


def mature_start(daily_intents_usd: pd.Series) -> pd.Timestamp | None:
    m = daily_intents_usd.rolling(30, min_periods=30).mean()
    hit = m[m > MATURE_THRESHOLD_USD]
    return None if hit.empty else hit.index.min()


def _block(w: pd.DataFrame, comps: list[str], real: list[str], measures: list[str],
           mature_from: pd.Timestamp | None = None) -> dict:
    w = w.copy()
    w["adoption"] = adoption_index(w, comps)
    w["real_usage"] = adoption_index(w, [c for c in real if c in w])
    g = growth(w)
    main_i = measures[0]
    res = {"q12": q1_q2(g, "real_usage", main_i),            # primary target (fix 2)
           "q12_adoption": q1_q2(g, "adoption", main_i),     # broad index, secondary
           "q12_robustness": {}}
    for i in measures[1:]:
        if i in g and g[i].notna().sum() >= 30:
            res["q12_robustness"][f"real_usage~{i}"] = q1_q2(g, "real_usage", i)
            res["q12_robustness"][f"adoption~{i}"] = q1_q2(g, "adoption", i)
    for c in list(dict.fromkeys(real + comps)):
        if c in g and g[c].notna().sum() >= 30:
            res["q12_robustness"][f"{c}~{main_i}"] = q1_q2(g, c, main_i)
    res["q3"] = q3(w, main_i, mature_from=mature_from)
    res["q3_usd"] = q3(w, main_i, value="fees_usd", mature_from=mature_from)
    res["answers"] = {"Q1": res["q12"]["q1"], "Q2": res["q12"]["q2"], "Q3": res["q3"]["verdict"],
                      "Q1_adoption": res["q12_adoption"]["q1"], "Q2_adoption": res["q12_adoption"]["q2"]}
    res["weeks"] = int(w["real_usage"].notna().sum())
    res["first_week"] = w.index[0].strftime("%Y-%m-%d")
    res["_w"] = w
    return res


def run(w: pd.DataFrame, comps: list[str], intents_measures: list[str],
        real: list[str] | None = None, mature_from: pd.Timestamp | None = None) -> dict:
    real = real or [c for c in REAL_USAGE if c in w]
    full = _block(w, comps, real, intents_measures, mature_from)
    out = {k: v for k, v in full.items() if k != "_w"}
    out["components"] = comps
    out["real_usage_components"] = real
    out["adoption_weekly"] = full["_w"]["adoption"]
    out["real_usage_weekly"] = full["_w"]["real_usage"]
    if mature_from is not None:                                  # fix 3: robustness window
        wm = w[w.index >= mature_from]
        if len(wm) >= 40:
            mb = _block(wm, comps, real, intents_measures, mature_from)
            out["mature"] = {k: v for k, v in mb.items() if k != "_w"}
            out["mature"]["from"] = pd.Timestamp(mature_from).strftime("%Y-%m-%d")
    return out
