# NEAR Valuation Check

**Is NEAR undervalued or overvalued?** A re-runnable model answers this from NEAR's own on-chain fundamentals,
with no peer chain required. Comparisons with other chains are an optional extra. Built for the NEAR HACKATHON
**Investment Thesis** track (`thesis`).

- **Dashboard:** https://almondxxx.github.io/nearthesis/ (refreshed daily from public data)
- **Thesis:** [`THESIS.md`](THESIS.md). Latest numbers: [`reports/latest.md`](reports/latest.md)
- **For AI reviewers:** [`AGENT.md`](AGENT.md)

## The problem
Bullish and bearish cases for NEAR both pick favourable numbers: account counts inflated by airdrop farming, DEX
volume quoted without revenue, or a chart picked to suit the argument. Neither can be checked or re-run. This
project scores NEAR's market cap against a fixed set of fundamentals, the same way every day. It publishes the
verdict, the code and the data.

## How the verdict works (NEAR only)
Three independent checks; the verdict is the majority view (Mixed if no two agree).

| Check | Question | Overvalued if | Undervalued if |
|---|---|---|---|
| **1. Fair value** | What would NEAR be worth at its own median multiples over the last 2 years? | market cap above the fair-value band | below the band |
| **2. Confidence Premium** | Is the market-cap percentile ahead of the fundamentals percentile (last 365 days)? | +15 or more | -15 or less |
| **3. Multiples vs history** | Where do today's multiples rank in NEAR's last 2 years (0-100)? | median rank 75 or more | 25 or less |

- **Fair value.** For each of five fundamentals, multiply today's figure by NEAR's median multiple over the last
  2 years. The fundamentals are revenue (fees burned), DEX volume, TVL, stablecoin supply and returning accounts.
  Fair value is the geometric mean of the five results. The band uses the 25th and 75th percentile multiples.
- **Confidence Premium.** Every input is scored as a percentile against NEAR's trailing 365 days:
  - Network: active accounts, returning accounts, transactions, fees.
  - DeFi: TVL, DEX volume, stablecoins.
  - Tokenomics: staked share, net supply growth, and the share of issuance offset by fee burn.

  The three pillars average into a **Fundamentals Index**. The market cap percentile is the **Valuation Index**.
  The premium is Valuation minus Fundamentals.
- **No look-ahead.** Every window looks backward only. A test checks this.
- **Reliability checks:** the premium recomputed under 2,000 random weightings, and the 90-day forward price change
  after each reading. The second is descriptive only.

### Result at the committed snapshot (2026-11-12)
| | |
|---|---|
| **Verdict** | **Overvalued** (2 of 3 checks) |
| Market cap / price | $4.70B / $3.59 |
| Fair value (band) | $2.52B, about $1.92 a token ($1.90B–$5.37B) |
| Confidence Premium | +28.6 (positive under 100% of 2,000 random weightings) |
| Multiples rank vs 2-year history | 76/100 |

NEAR trades at its usual multiple of DEX flow, which is 93% NEAR Intents and up 17x in two years. But it trades at
2–3x its usual multiple of revenue, stablecoins and returning users. Details in [`THESIS.md`](THESIS.md).

## Optional comparisons
None of these affect the verdict. On the dashboard they are behind a "Compare with" toggle:
- **AVAX**: a similar-sized L1.
- **THORChain**: the same business as NEAR Intents (cross-chain swaps).
- **L1 basket median**: AVAX, Sui, Aptos, TON, ICP and Cardano, as a market-wide control.
- **Pump.fun event study**: Pump.fun's app added NEAR tokens on 2026-11-04 and Avalanche tokens right after (2026-11-05,
  approximate). The chart indexes each chain to its own 14 days before go-live, against a control group of L1s
  Pump.fun didn't add.

## Try it

**Requirements:** Python 3.10+.

**1. Rebuild from the committed snapshot. Offline, deterministic, about 15 seconds.**
```bash
pip install -r requirements.txt
python run.py --offline
```
You should see each chain's fundamentals, valuation and premium printed, and `docs/data/dashboard.json`,
`data/processed/*.csv` and `reports/latest.md` regenerated. The report opens with the NEAR verdict.

**2. Run the tests.**
```bash
python -m unittest discover -s tests -v
```
All tests should pass. They cover no look-ahead, the weighting maths, the fair-value maths, the verdict majority
rule, and the payload shape.

**3. Open the dashboard.**
```bash
python -m http.server -d docs 8000
```
Open http://localhost:8000.
- **At the top:** the verdict and the three checks. Below them, the market cap vs fair-value band chart, the verdict
  history, the multiples table, the premium and pillar charts, the raw metrics, and the reliability tables.
- **"Compare with" buttons** (AVAX, THORChain, L1 basket): each adds that peer to a multiples chart and a table.
- **Pump.fun section:** choose a metric to see NEAR, AVAX and the control group indexed around go-live.

**4. Fetch fresh data. Needs internet, no API keys.**
```bash
python run.py
```
You should see `data/raw/` updated to yesterday (UTC), with all outputs rebuilt.

## How the dashboard stays live
`.github/workflows/refresh.yml` runs daily at 02:17 UTC, on demand, and on code pushes. Each run:
1. fetches fresh data;
2. rebuilds the outputs and runs the tests;
3. commits the new snapshot;
4. redeploys `docs/` to GitHub Pages.

The page reads `data/dashboard.json` when it loads, so the verdict, charts and tables follow the data with no code
change. The Pump.fun window also grows by one day per run. If a source is down, the run falls back to the last
committed snapshot.

One-time setup: **Settings → Pages → Source: GitHub Actions**.

## Data sources
All public, no keys, so anyone can re-run the pipeline.

| Data | Source |
|---|---|
| NEAR price, market cap, supply, txns, fees, active and new accounts | NearBlocks `api.nearblocks.io/v1/charts` |
| NEAR total stake (one snapshot per run) | NEAR RPC `validators` |
| TVL, DEX volume, stablecoins, fees, revenue (NEAR and peers) | DefiLlama |
| AVAX C-chain activity and staking | Avalanche Data API `metrics.avax.network` |
| Peer market caps (last 365 days), AVAX supply | CoinGecko public API |
| AVAX price history | DefiLlama `coins.llama.fi` |

**Definitions.**
- **Revenue** is fees burned: 70% of NEAR fees (the other 30% goes to contract developers).
- **Active accounts** are daily distinct signers.
- **Returning accounts** are active minus new.
- **Flows** are 30-day averages, annualised.

**Known limits.**
- **NEAR stake history** isn't available without an API key, so the pipeline saves one snapshot per run. The
  staking score joins the index once 180 snapshots exist.
- **Peer market caps** cover only the last 365 days.
- **The Pump.fun go-live dates** come from secondary reports, and AVAX's is approximate.
- **No protocol buyback** exists on NEAR, so burn is the only supply sink measured.

**Why not Dune?** Dune has good NEAR tables, but running queries needs an API key and credits. Judges need to be able
to re-run this, so every input comes from keyless APIs.

## Repository layout
```
run.py                     CLI: fetch + build (or --offline)
pipeline/sources.py        one fetcher per source -> data/raw/*.csv
pipeline/build.py          panels, percentile scores, pillars, Fundamentals/Valuation indices, premium
pipeline/valuation.py      NEAR-only: fair value, multiples vs history, verdict
pipeline/compare.py        optional: peer multiples, growth, Pump.fun event study
pipeline/report.py         renders reports/latest.md
data/raw/                  committed source snapshot (refreshed daily by CI)
data/processed/            daily panels, NEAR valuation series
docs/index.html            dashboard (Plotly), reads docs/data/dashboard.json
THESIS.md  AGENT.md  LICENSE  tests/
```

## Hackathon disclosure
- Built during the NEAR HACKATHON window (all commits are from November 2026). This is a new repository with no pre-hackathon code.
- Libraries: pandas, numpy, requests (Python), and plotly.js 2.34 loaded from cdnjs.
- AI assistance: developed with Claude Code.
- License: [MIT](LICENSE).

This is research, not investment advice.
