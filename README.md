# NEAR Confidence Index

A re-runnable model that measures **how much confidence investors place in NEAR, and whether NEAR's on-chain
fundamentals justify it**, with Avalanche (C-chain) as the peer. Built for the NEAR HACKATHON
**Investment Thesis** track (`thesis`).

- **Dashboard:** https://almondxxx.github.io/nearthesis/ (refreshed daily from public data)
- **Thesis:** [`THESIS.md`](THESIS.md). Latest numbers: [`reports/latest.md`](reports/latest.md)
- **For AI reviewers:** [`AGENT.md`](AGENT.md)

## The problem
Investment cases for NEAR usually pick favourable metrics, such as account counts inflated by airdrop farming,
or DEX volume quoted without fees. That makes them hard to check and impossible to re-run. This project fixes a
small set of comparable metrics and scores them the same way for NEAR and AVAX. It publishes one number,
the **Confidence Premium**, and the code and data that produce it.

## What it computes
For each chain, every day:

| Pillar | Metrics |
|---|---|
| Network | active accounts (daily signers), returning accounts (active - new), transactions, fees (USD) |
| DeFi | TVL, DEX volume, stablecoin supply |
| Tokenomics | staked share of circulating supply, net supply growth (lower scores higher), share of gross issuance offset by fee burn |
| Valuation | market cap; also reported: FDV, market cap / revenue, / fees, / TVL, / DEX volume, / stablecoins, per active account |

1. Each metric is smoothed with a 7-day mean (log scale for sizes). It is then scored as a **percentile (0-100)
   against that chain's trailing 365 days**. The score uses past data only, so there is no look-ahead.
2. Pillar = equal-weight mean of its metrics. **Fundamentals Index** = equal-weight mean of the three pillars.
3. **Valuation Index** = the same percentile applied to market cap.
4. **Confidence Premium = Valuation - Fundamentals.** Above 0, investors pay ahead of fundamentals.
   Below 0, the price lags them.
5. Cross-chain comparison uses multiples: NEAR's multiple divided by AVAX's, as a daily time series.
6. A **robustness check** recomputes the premium under 2,000 random weightings.
   A **descriptive backtest** shows 90-day forward price changes for each premium bucket.

### Result at the committed snapshot (2026-11-12)
| | NEAR | AVAX |
|---|---:|---:|
| Fundamentals Index | 57.7 | 20.0 |
| Valuation Index | 86.3 | 29.9 |
| Confidence Premium | +28.6 | +9.9 |
| Market cap / revenue (fees burned) | 4,202x | 910x |
| DEX volume, annualised | $49.3B | $30.5B |

The short version: NEAR's premium comes from DeFi flow, 93% of it through NEAR Intents, which grew 17x in
two years. That flow isn't reaching L1 revenue: fees fell, and burn offsets under 1% of issuance. See [`THESIS.md`](THESIS.md).

## Try it

**Requirements:** Python 3.10+.

**1. Rebuild from the committed snapshot. Offline, deterministic, about 10 seconds.**
```bash
pip install -r requirements.txt
python run.py --offline
```
You should see two lines with each chain's fundamentals, valuation and Confidence Premium.
`docs/data/dashboard.json` and `reports/latest.md` are regenerated.

**2. Run the tests.**
```bash
python -m unittest discover -s tests -v
```
You should see 10 tests pass. They cover no look-ahead, the weighting maths, and the payload shape and ranges.

**3. Open the dashboard locally.**
```bash
python -m http.server -d docs 8000
```
Open http://localhost:8000. You should see the KPI tiles for both chains, then these charts:
- Confidence Premium over time
- Fundamentals vs Valuation for each chain
- the pillar breakdown (switch NEAR/AVAX)
- the raw-metric explorer (choose a metric)
- NEAR ÷ AVAX multiples (choose a multiple)

Below the charts are the snapshot table, the robustness table and the backtest table.

**4. Fetch fresh data. Needs internet, no API keys.**
```bash
python run.py
```
You should see the snapshot in `data/raw/` updated to yesterday (UTC), with all outputs rebuilt.

## How the dashboard stays live
`.github/workflows/refresh.yml` runs daily at 02:17 UTC, on demand, and on code pushes. Each run:
1. fetches fresh data;
2. rebuilds the index and runs the tests;
3. commits the new snapshot (`data/`, `docs/data/`, `reports/`);
4. redeploys `docs/` to GitHub Pages.

The page reads `data/dashboard.json` when it loads, so every chart, tile and table changes with the data, with no
code change. If a source is down, the run falls back to the last committed snapshot.

One-time setup: **Settings → Pages → Source: GitHub Actions**.

## Data sources
All public, no keys, so anyone can re-run the pipeline.

| Data | Source |
|---|---|
| NEAR price, market cap, supply, txns, fees, active and new accounts | NearBlocks `api.nearblocks.io/v1/charts` |
| NEAR total stake (one snapshot per run) | NEAR RPC `validators` |
| AVAX C-chain active senders, txns, fees burned, cumulative addresses; P-chain staking weight | Avalanche Data API `metrics.avax.network` |
| AVAX price history | DefiLlama `coins.llama.fi` |
| AVAX circulating and total supply | CoinGecko public API |
| TVL, DEX volume, stablecoins, fees, revenue (both chains) | DefiLlama |

**Definitions.**
- **Revenue** is fees burned: 70% of NEAR fees (the other 30% goes to contract developers) and 100% of AVAX C-chain fees.
- **AVAX** means the C-chain only.
- **Neither chain has a protocol-level buyback,** so burn is the only supply sink measured.

**Known limits.**
- **NEAR stake history** isn't available without an API key, so the pipeline saves one snapshot per run.
  The NEAR staking score joins the index on its own once 180 snapshots exist.
- **AVAX circulating supply** before CoinGecko's 365-day window is extrapolated and flagged. It is used only
  for market cap.
- **Activity counts** on both chains are distorted by bots and campaigns. That is why each chain is scored only
  against its own history, and why returning accounts are tracked separately.

**Why not Dune?** Dune has good NEAR and Avalanche tables, but running queries needs an API key and credits.
Judges need to be able to re-run this, so every input comes from keyless APIs.

## Repository layout
```
run.py                     CLI: fetch + build (or --offline)
pipeline/sources.py        one fetcher per data source -> data/raw/*.csv
pipeline/build.py          panels, scores, indices, multiples, sensitivity, backtest
pipeline/report.py         renders reports/latest.md
data/raw/                  committed source snapshot (refreshed daily by CI)
data/processed/            per-chain daily panels with every score
docs/index.html            dashboard (Plotly), reads docs/data/dashboard.json
reports/latest.md          auto-generated numbers
THESIS.md                  the written thesis
AGENT.md                   guide for AI agents and reviewers
tests/                     unittest suite
```

## Hackathon disclosure
- Built during the NEAR HACKATHON window (all commits are from November 2026). This is a new repository with no
  pre-hackathon code.
- Libraries: pandas, numpy, requests (Python), and plotly.js 2.34 loaded from cdnjs.
- AI assistance: developed with Claude Code.
- License: [MIT](LICENSE).

This is research, not investment advice.
