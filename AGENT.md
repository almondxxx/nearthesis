# AGENT.md

Instructions for AI coding agents (Claude Code, Codex and others) that review, run or extend this repo.

## What this repo is
A re-runnable investment-thesis model for NEAR, compared with AVAX (C-chain). A Python pipeline pulls public,
keyless data and scores each chain on **network**, **DeFi** and **tokenomics** pillars. It combines them into a
**Fundamentals Index**, compares that with a **Valuation Index** (market cap), and publishes the gap as the
**Confidence Premium**. A static dashboard (`docs/`) renders the result.

## Verify it in about 2 minutes
```bash
pip install -r requirements.txt
python run.py --offline                       # rebuild from committed data/raw/; no network needed
python -m unittest discover -s tests -v       # 10 tests should pass
python -m http.server -d docs 8000            # open http://localhost:8000
```
`python run.py` (without `--offline`) fetches fresh data first. It needs network access to api.nearblocks.io,
metrics.avax.network, api.llama.fi, coins.llama.fi, stablecoins.llama.fi, api.coingecko.com and rpc.mainnet.near.org.

Expected: `run.py` prints both chains' fundamentals, valuation and premium, and writes
`docs/data/dashboard.json` and `reports/latest.md`. Every figure in `THESIS.md` can be traced to
`data/processed/{near,avax}_daily.csv` or `reports/latest.md` at the same snapshot date.

## Layout
| Path | Role | Edit by hand? |
|---|---|---|
| `pipeline/sources.py` | One fetcher per source, writes `data/raw/*.csv` | yes |
| `pipeline/build.py` | Panels, scoring, indices, multiples, sensitivity; writes outputs | yes |
| `pipeline/report.py` | Renders `reports/latest.md` | yes |
| `run.py` | CLI entry point | yes |
| `docs/index.html` | Dashboard; reads `docs/data/dashboard.json` at load time | yes |
| `data/raw/` | Committed source snapshot (also refreshed daily by CI) | **no**, except by fetchers |
| `data/raw/near_staking_snapshots.csv` | Append-only NEAR stake history, one row per run | **never rewrite history** |
| `data/processed/`, `docs/data/`, `reports/latest.md` | Generated | **no** |
| `THESIS.md` | Human-written conclusion, pinned to a snapshot date | yes, keep the numbers in sync |
| `.github/workflows/refresh.yml` | Daily fetch, build, test, commit, Pages deploy | yes |

## Invariants: don't break these
- **No look-ahead.** Scores use `rolling_pct`, which only sees the trailing window. `test_no_lookahead` checks this.
- **No API keys or secrets** in the repo or the pipeline. Every source must stay public and keyless so anyone can re-run it.
- **Deterministic builds.** Same `data/raw/` gives the same outputs (the sensitivity analysis uses a fixed seed).
- **Like-for-like definitions.** Revenue = fees burned (NEAR 70%, AVAX C-chain 100%). Active accounts = daily signers.
  AVAX = C-chain only. If you change a definition, update `LABELS`, the dashboard method section and `THESIS.md`.
- **Don't invent data.** Leave unknown values as NaN or `null`. Never fill a series with made-up numbers. The one
  estimate (AVAX circulating supply before CoinGecko's 365-day window) is flagged as `supply_estimated` and is used only for market cap.
- Dashboard: one y-axis per chart, NEAR is always blue and AVAX always orange, and the page must work at 390px width.

## Add a metric
1. Fetch it in `pipeline/sources.py` (in the right `*_llama`, `near_*` or `avax_*` frame) and confirm it lands in `data/raw/`.
2. Derive it per chain in `near_panel()` / `avax_panel()` in `pipeline/build.py`.
3. Register it in `METRICS` as `(pillar, higher_is_better, log_transform)` and in `LABELS`.
4. Add it to the metric list in `docs/index.html` (and `ROWS` in `report.py` if it belongs in the snapshot).
5. Run `python run.py --offline && python -m unittest discover -s tests`.

## Reviewer checklist (hackathon screening)
- [ ] `python run.py --offline` succeeds and prints both chains' indices.
- [ ] Tests pass.
- [ ] The dashboard loads with no console errors and shows the Confidence Premium, pillar and multiple charts.
- [ ] `THESIS.md` numbers match `reports/latest.md` for the snapshot date stated at the top.
- [ ] Every data source in the README is public and needs no key.
