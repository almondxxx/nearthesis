"""Render reports/latest.md from the dashboard payload. Regenerated on every
pipeline run, so the numbers quoted here always match the dashboard."""
from __future__ import annotations

from pathlib import Path


def _usd(v):
    if v is None:
        return "n/a"
    a = abs(v)
    for div, suf in [(1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if a >= div:
            return f"${v / div:,.2f}{suf}"
    return f"${v:,.2f}"


def _x(v):
    return "n/a" if v is None else (f"{v:,.2f}x" if abs(v) < 10 else f"{v:,.1f}x")


def _pct(v, signed=False):
    if v is None:
        return "n/a"
    return f"{v * 100:+.1f}%" if signed else f"{v * 100:.1f}%"


def _num(v):
    return "n/a" if v is None else f"{v:,.0f}"


def _read_premium(p):
    if p is None:
        return "n/a"
    if p <= -15:
        return "valuation lags fundamentals (market confidence below what usage supports)"
    if p >= 15:
        return "valuation runs ahead of fundamentals (confidence premium)"
    return "valuation roughly in line with fundamentals"


ROWS = [
    ("Price", "price_usd", _usd),
    ("Market cap", "market_cap_usd", _usd),
    ("Fully diluted value", "fdv_usd", _usd),
    ("Fees, annualised (30d)", "fees_ann_usd", _usd),
    ("Revenue = fees burned, annualised (30d)", "revenue_ann_usd", _usd),
    ("DeFi TVL", "tvl_usd", _usd),
    ("DEX volume, annualised (30d)", "dex_volume_ann_usd", _usd),
    ("Stablecoin supply", "stablecoins_usd", _usd),
    ("Active accounts / day (30d avg)", "active_accounts_30d", _num),
    ("Returning share of active (30d)", "retention_ratio_30d", _pct),
    ("Transactions / day (30d avg)", "txns_30d_avg", _num),
    ("Staked share of circulating", "staking_ratio", _pct),
    ("Net supply growth, last 365d", "net_issuance_365d", lambda v: _pct(v, True)),
    ("Net supply growth, annualised (last 30d)", "net_issuance_ann", lambda v: _pct(v, True)),
    ("Gross issuance offset by burn (30d)", "burn_offset_30d", _pct),
    ("**Market cap / revenue**", "mc_to_revenue", _x),
    ("Market cap / fees", "mc_to_fees", _x),
    ("Market cap / TVL", "mc_to_tvl", _x),
    ("FDV / TVL", "fdv_to_tvl", _x),
    ("Market cap / DEX volume", "mc_to_dex_volume", _x),
    ("Market cap / stablecoins", "mc_to_stablecoins", _x),
    ("Market cap per active account", "mc_per_active_account", _usd),
    ("Revenue per active account (annual)", "revenue_per_active_account", _usd),
    ("YoY active accounts", "yoy_active_accounts", lambda v: _pct(v, True)),
    ("YoY transactions", "yoy_txns", lambda v: _pct(v, True)),
    ("YoY fees", "yoy_fees_usd", lambda v: _pct(v, True)),
    ("YoY TVL", "yoy_tvl_usd", lambda v: _pct(v, True)),
    ("YoY DEX volume", "yoy_dex_volume_usd", lambda v: _pct(v, True)),
    ("YoY stablecoins", "yoy_stablecoins_usd", lambda v: _pct(v, True)),
    ("YoY market cap", "yoy_market_cap_usd", lambda v: _pct(v, True)),
]


def write_report(d: dict, path: Path) -> None:
    m, L, S, sens = d["meta"], d["latest"], d["snapshot"], d["sensitivity"]
    lines = [
        "# NEAR vs AVAX - latest numbers",
        "",
        f"_Generated automatically by `python run.py`. Data as of **{m['as_of']}** (fetched {m['fetched_at']}). "
        "Do not edit by hand: the next pipeline run overwrites this file._",
        "",
        "## Indices (0-100, percentile vs the chain's own trailing 365 days)",
        "",
        "| | NEAR | AVAX |",
        "|---|---:|---:|",
    ]
    for k, lab in [("network", "Network pillar"), ("defi", "DeFi pillar"), ("tokenomics", "Tokenomics pillar"),
                   ("fundamentals", "**Fundamentals Index**"), ("valuation", "**Valuation Index**"),
                   ("confidence_premium", "**Confidence Premium** (Valuation - Fundamentals)")]:
        lines.append(f"| {lab} | {L['near'].get(k)} | {L['avax'].get(k)} |")
    lines += [
        "",
        f"- NEAR: {_read_premium(L['near'].get('confidence_premium'))}.",
        f"- AVAX: {_read_premium(L['avax'].get('confidence_premium'))}.",
        "",
        f"### Robustness ({sens['draws']} random weightings of pillars and metrics)",
        "",
        "| | median | 5th pct | 95th pct | share of draws < 0 |",
        "|---|---:|---:|---:|---:|",
    ]
    for k, lab in [("near", "NEAR premium"), ("avax", "AVAX premium"), ("near_minus_avax", "NEAR minus AVAX")]:
        s = sens[k]
        lines.append(f"| {lab} | {s['median']} | {s['p05']} | {s['p95']} | {s['share_negative'] * 100:.0f}% |")
    lines += [
        "",
        "### Does the premium predict returns? (90-day forward price change, descriptive)",
        "",
        "| Chain | Bucket | Days | Median | Mean | Share positive |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for c in ("near", "avax"):
        for r in d["backtest"]["rows"][c]:
            lines.append(f"| {c.upper()} | {r['bucket']} | {r['days']} | {_pct(r['median'], True)} | {_pct(r['mean'], True)} | {_pct(r['hit_rate'])} |")
    lines += [
        "",
        "Overlapping windows over a single two-year regime: read this as a description, not a trading signal.",
        "",
        "## Cross-chain snapshot (trailing 30 days)",
        "",
        "| Metric | NEAR | AVAX | NEAR / AVAX |",
        "|---|---:|---:|---:|",
    ]
    for lab, key, fmt in ROWS:
        a, b = S["near"].get(key), S["avax"].get(key)
        ratio = f"{a / b:.2f}" if (a is not None and b not in (None, 0) and not key.startswith(("yoy", "net_"))) else ""
        lines.append(f"| {lab} | {fmt(a)} | {fmt(b)} | {ratio} |")
    lines += [
        "",
        "Notes: AVAX figures are the C-chain (Avalanche L1s excluded). Active accounts = daily distinct signers "
        "(NEAR: NearBlocks; AVAX: `activeSenders`). Revenue = fees burned: 70% of NEAR fees "
        "(30% go to contract developers), 100% of AVAX C-chain fees. AVAX FDV uses today's total supply. "
        f"NEAR staking history is collected one snapshot per run ({m['near_staking_snapshots']} so far), "
        "so NEAR's staking score starts once enough snapshots accrue.",
        "",
    ]
    path.write_text("\n".join(lines))
