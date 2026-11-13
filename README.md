# NEAR Intents Usage Test

An evidence-first investment thesis for the NEAR HACKATHON **Investment Thesis** track (`thesis`).

**Hypothesis under test:** *cross-chain volume through NEAR Intents is a better leading indicator of real
network usage than the NEAR token price.* The repo tests that claim and reports what the data says, including
anything that cuts against it.

- **Dashboard:** https://almondxxx.github.io/nearthesis/. Every chart shows the query behind it and one plain
  sentence on what it shows. The page is rebuilt daily from raw data.
- **Thesis:** [`THESIS.md`](THESIS.md): the claim, evidence for, evidence against, what would change my mind, and
  what can't be computed.
- **Latest numbers:** [`reports/thesis_results.md`](reports/thesis_results.md), generated on every run.
- **For AI reviewers:** [`AGENT.md`](AGENT.md)
- **Appendix:** [`docs/valuation.html`](docs/valuation.html), a separate check of whether NEAR's market cap is
  rich or cheap against its own fundamentals.

## One command rebuilds everything
```bash
pip install -r requirements.txt
python run.py --offline     # rebuild every chart from the committed raw data (no keys, about 20 s)
python run.py               # fetch fresh data first (keys optional, see below)
```
You should see a line like `thesis: <start> to <end>, <N> weeks -> hypothesis <RESULT>`. These files are
regenerated:
- `docs/data/thesis.json` and `reports/thesis_results.md` (the main thesis);
- `docs/data/dashboard.json` and `reports/latest.md` (the appendix);
- the daily and weekly tables in `data/processed/`.

Then open the dashboard:
```bash
python -m http.server -d docs 8000
```
Open http://localhost:8000. You should see the result box, the data charts (each with an expandable "Query behind
this chart"), the lead-lag chart (choose a usage measure), and the predictive-test table.

Run the tests:
```bash
python -m unittest discover -s tests -v
```
All tests should pass. They include a check that the method **detects a real one-week lead in synthetic data and
doesn't invent one in pure noise**.

## Data sources
| Data | Source | Key |
|---|---|---|
| Daily active accounts, transactions, contract usage, calls to `intents.near` | BigQuery `bigquery-public-data.crypto_near_mainnet_us` (SQL in [`sql/`](sql/), always filtered on `block_date`) | GCP service account |
| NEAR Intents swaps (1Click), sampled | NEAR Intents Explorer API `explorer.near-intents.org/api/v0/transactions` | `NEAR_INTENTS_JWT` |
| NEAR Intents daily USD volume, complete | DefiLlama `api.llama.fi/summary/dexs/near-intents` | none |
| NEAR price; active accounts and transactions when BigQuery is stale | NearBlocks `api.nearblocks.io/v1/charts` | none |
| BTC price (market control) | DefiLlama coins API | none |

**Keys.** Copy `.env.example` to `.env`. Without a key, that source's committed data in `data/raw/` is used, so the
rebuild still works.
- `NEAR_INTENTS_JWT` comes from the [Partner Dashboard](https://partners.near-intents.org).
- For BigQuery, use a service account with the *BigQuery Job User* role. Point `GOOGLE_APPLICATION_CREDENTIALS` at
  its key file, or set `GCP_SA_KEY_B64`. Every query is dry-run first and refused above `BQ_MAX_GB` (default 150 GB).

**Two limits that shape the method:**
1. **BigQuery may be stale.** NEAR Lake, the dataset's source, was deprecated on 2026-03-24. `sql/00_freshness.sql`
   checks the newest partition. Usage after that date comes from NearBlocks and is labelled as such.
2. **The Explorer API allows 1 request every 5 seconds.** At about 30,000 swaps a day, a full history would take
   about 36 hours. So swaps are counted in **2 random UTC hours per day**, seeded by date so the sample is
   reproducible, and scaled by 24. The sample is cached and resumable, and the daily job tops it up.
   DefiLlama provides the complete USD series.

## How the test works
- **Weekly log growth, not levels.** Shared long-run trends can't create a fake relationship.
- **Three tests, fixed before looking at results:**
  1. lead-lag correlation, 0–8 weeks ahead;
  2. an in-sample F-test: do 2 weekly lags of the predictor add information beyond usage's own lags and BTC?
  3. next-week forecasts on an expanding window, compared with a baseline without the predictor.
- **Verdict rule:** Intents wins a usage measure only if it passes test 2, improves test 3, and beats price on
  test 3. The rule is coded in [`pipeline/hypothesis.py`](pipeline/hypothesis.py).

## Repository layout
```
run.py                    one command: fetch (optional) + rebuild everything
sql/                      BigQuery SQL (freshness, daily activity, contract usage)
pipeline/bq.py            runs sql/ with dry-run cost guard, incremental cache
pipeline/intents.py       Explorer API hour sampler (rate-limited, resumable)
pipeline/sources.py       NearBlocks, DefiLlama, BTC, and appendix sources
pipeline/hypothesis.py    weekly growth, lead-lag, predictive and out-of-sample tests, verdict rule
pipeline/thesis.py        builds docs/data/thesis.json (charts + queries + sentences) and reports/thesis_results.md
pipeline/build.py, valuation.py, report.py   appendix: valuation check
docs/index.html           dashboard (main thesis);  docs/valuation.html  appendix
data/raw/                 committed raw data (refreshed daily by GitHub Actions)
tests/                    unittest suite
```

## How it stays current
`.github/workflows/refresh.yml` runs daily. It fetches fresh data with the `NEAR_INTENTS_JWT` and `GCP_SA_KEY_JSON`
repository secrets, rebuilds, tests, commits the new data and redeploys `docs/` to GitHub Pages.

One-time setup: **Settings → Pages → Source: GitHub Actions**.

## Hackathon disclosure
- Built during the NEAR HACKATHON window (all commits are from November 2026). This is a new repository with no
  pre-hackathon code.
- Libraries: pandas, numpy, scipy, statsmodels, requests and google-cloud-bigquery (Python), and plotly.js 2.34
  loaded from cdnjs.
- AI assistance: developed with Claude Code.
- License: [MIT](LICENSE).

This is research, not investment advice.
