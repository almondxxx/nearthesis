"""Fetchers for every public, keyless data source the thesis uses.

Each fetcher returns a tidy DataFrame indexed by UTC date. `fetch_all()` writes
one CSV per source to data/raw/ so the rest of the pipeline (and judges) can run
fully offline from the committed snapshot.

Sources
-------
NEAR   : NearBlocks charts API  (price, market cap, supply, txns, fees, accounts)
AVAX   : Avalanche Data API     (C-chain active addresses, txns, fees burned,
                                  cumulative addresses; P-chain staking weight)
AVAX   : CoinGecko public API   (365d market cap -> circulating supply)
AVAX   : DefiLlama coins API    (price history)
Both   : DefiLlama              (chain TVL, DEX volume, stablecoins, fees, revenue)
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# 2 years displayed + 1 year of warm-up for the trailing-365-day percentiles.
START = pd.Timestamp("2023-11-01")
START_TS = int(START.timestamp())

UA = {"User-Agent": "nearthesis-pipeline/1.0 (+public research)"}
YOCTO = 1e24
NAVAX = 1e9

LLAMA_CHAINS = {"near": "Near", "avax": "Avalanche"}
LLAMA_SLUGS = {"near": "near", "avax": "avalanche"}


def _get(url: str, params: dict | None = None, tries: int = 4) -> dict | list:
    last = None
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=60)
            if r.status_code == 429:
                time.sleep(10 * (i + 1))
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:  # network blips
            last = e
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"GET {url} failed after {tries} tries: {last}")


def _from_unix(series) -> pd.DatetimeIndex:
    return pd.to_datetime(pd.Series(series).astype("int64"), unit="s").dt.normalize()


# ---------------------------------------------------------------- NEAR ----
def near_nearblocks() -> pd.DataFrame:
    rows = _get("https://api.nearblocks.io/v1/charts")["charts"]
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None).dt.normalize()
    num = lambda c: pd.to_numeric(df[c], errors="coerce")
    out = pd.DataFrame(
        {
            "date": df["date"],
            "price_usd": num("near_price"),
            "market_cap_usd": num("market_cap"),
            "total_supply": num("total_supply") / YOCTO,
            "circulating_supply": num("circulating_supply") / YOCTO,
            "txns": num("txns"),
            "fees_native": num("txn_fee") / YOCTO,
            "fees_usd_nearblocks": num("txn_fee_usd"),
            "active_accounts": num("active_accounts"),
            "new_accounts": num("new_accounts"),
        }
    )
    return out[out["date"] >= START].set_index("date").sort_index()


# ---------------------------------------------------------------- AVAX ----
def _avax_metric(path: str, params: dict) -> pd.Series:
    url = f"https://metrics.avax.network/v2/{path}"
    params = {**params, "pageSize": 1000, "startTimestamp": START_TS}
    out, token = [], None
    for _ in range(20):
        p = dict(params)
        if token:
            p["pageToken"] = token
        d = _get(url, p)
        out += d.get("results", [])
        token = d.get("nextPageToken")
        if not token:
            break
    if not out:
        return pd.Series(dtype=float)
    s = pd.Series({pd.Timestamp(r["timestamp"], unit="s").normalize(): r["value"] for r in out})
    return s.sort_index()


def avax_chain_metrics() -> pd.DataFrame:
    c = "chains/43114/metrics"
    day = {"timeInterval": "day"}
    df = pd.DataFrame(
        {
            "active_accounts": _avax_metric(f"{c}/activeAddresses", day),
            "active_senders": _avax_metric(f"{c}/activeSenders", day),
            "txns": _avax_metric(f"{c}/txCount", day),
            "fees_native": _avax_metric(f"{c}/feesPaid", day),
            "cumulative_addresses": _avax_metric(f"{c}/cumulativeAddresses", day),
        }
    )
    df["new_accounts"] = df["cumulative_addresses"].diff()
    stake = pd.DataFrame(
        {
            "validator_weight": _avax_metric("networks/mainnet/metrics/validatorWeight", {}) / NAVAX,
            "delegator_weight": _avax_metric("networks/mainnet/metrics/delegatorWeight", {}) / NAVAX,
        }
    )
    stake["staked"] = stake["validator_weight"] + stake["delegator_weight"]
    df = df.join(stake[["staked"]], how="outer")
    df.index.name = "date"
    return df[df.index >= START].sort_index()


def avax_market() -> pd.DataFrame:
    # Price: DefiLlama coins chart, in 400-day chunks (API span limit).
    prices = {}
    start = START_TS
    now = int(time.time())
    while start < now:
        d = _get(
            "https://coins.llama.fi/chart/coingecko:avalanche-2",
            {"start": start, "span": 400, "period": "1d"},
        )
        pts = d["coins"]["coingecko:avalanche-2"]["prices"]
        for p in pts:
            prices[pd.Timestamp(p["timestamp"], unit="s").normalize()] = p["price"]
        if not pts:
            break
        start = pts[-1]["timestamp"] + 3600
        if len(pts) < 400:
            break
    price = pd.Series(prices).sort_index()

    # Circulating supply: CoinGecko public API (last 365 days only).
    cg = _get(
        "https://api.coingecko.com/api/v3/coins/avalanche-2/market_chart",
        {"vs_currency": "usd", "days": 365, "interval": "daily"},
    )
    cg_px = pd.Series({pd.Timestamp(t, unit="ms").normalize(): v for t, v in cg["prices"]})
    cg_mc = pd.Series({pd.Timestamp(t, unit="ms").normalize(): v for t, v in cg["market_caps"]})
    cg_mc = cg_mc.groupby(level=0).last()
    cg_px = cg_px.groupby(level=0).last()
    circ = (cg_mc / cg_px).replace([float("inf")], float("nan")).dropna()

    meta = _get(
        "https://api.coingecko.com/api/v3/coins/avalanche-2",
        {"localization": "false", "tickers": "false", "community_data": "false", "developer_data": "false"},
    )["market_data"]

    df = pd.DataFrame({"price_usd": price, "circulating_supply_cg": circ})
    df["total_supply_snapshot"] = float(meta["total_supply"])
    df.index.name = "date"
    return df[df.index >= START].sort_index()


# ---------------------------------------------------------- DefiLlama ----
def llama(chain: str) -> pd.DataFrame:
    name, slug = LLAMA_CHAINS[chain], LLAMA_SLUGS[chain]

    tvl = _get(f"https://api.llama.fi/v2/historicalChainTvl/{name}")
    tvl = pd.Series({pd.Timestamp(r["date"], unit="s").normalize(): r["tvl"] for r in tvl})

    def dim(url):
        d = _get(url, {"excludeTotalDataChartBreakdown": "true"})
        return pd.Series({pd.Timestamp(t, unit="s").normalize(): v for t, v in d.get("totalDataChart", [])})

    dex = dim(f"https://api.llama.fi/overview/dexs/{slug}")
    fees = dim(f"https://api.llama.fi/summary/fees/{slug}?dataType=dailyFees")
    rev = dim(f"https://api.llama.fi/summary/fees/{slug}?dataType=dailyRevenue")

    st = _get(f"https://stablecoins.llama.fi/stablecoincharts/{name}")
    stable = pd.Series(
        {
            pd.Timestamp(int(r["date"]), unit="s").normalize(): sum((r.get("totalCirculatingUSD") or {}).values())
            for r in st
        }
    )

    df = pd.DataFrame(
        {"tvl_usd": tvl, "dex_volume_usd": dex, "fees_usd": fees, "revenue_usd": rev, "stablecoins_usd": stable}
    )
    df = df.groupby(level=0).last()
    df.index.name = "date"
    return df[df.index >= START].sort_index()


# -------------------------------------------------------------- driver ----
def near_staking_snapshot() -> dict:
    """Current total stake of active NEAR validators (RPC). History is not
    available keylessly, so each pipeline run appends one row to
    data/raw/near_staking_snapshots.csv and the series grows over time."""
    d = _get_rpc({"jsonrpc": "2.0", "id": 1, "method": "validators", "params": [None]})
    staked = sum(int(v["stake"]) for v in d["result"]["current_validators"]) / YOCTO
    # Stamped with the last complete UTC day, the latest day the panels keep.
    day = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize() - pd.Timedelta(days=1)
    return {"date": day.strftime("%Y-%m-%d"), "staked": staked}


def _get_rpc(body: dict) -> dict:
    for i in range(4):
        try:
            r = requests.post("https://rpc.mainnet.near.org", json=body, headers=UA, timeout=60)
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            time.sleep(3 * (i + 1))
    raise RuntimeError("NEAR RPC unavailable")


def fetch_all(raw_dir: Path = RAW_DIR) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    jobs = {
        "near_nearblocks": near_nearblocks,
        "avax_chain": avax_chain_metrics,
        "avax_market": avax_market,
        "near_llama": lambda: llama("near"),
        "avax_llama": lambda: llama("avax"),
    }
    for name, fn in jobs.items():
        print(f"fetch {name} ...", flush=True)
        fn().to_csv(raw_dir / f"{name}.csv", float_format="%.6f")

    snap_path = raw_dir / "near_staking_snapshots.csv"
    snap = near_staking_snapshot()
    hist = pd.read_csv(snap_path, dtype={"date": str}) if snap_path.exists() else pd.DataFrame(columns=["date", "staked"])
    hist = pd.concat([hist, pd.DataFrame([snap])]).drop_duplicates("date", keep="last").sort_values("date")
    hist.to_csv(snap_path, index=False, float_format="%.3f")

    (raw_dir / "FETCHED_AT").write_text(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + "\n")
