# AGENT.md

Instructions for AI agents (Claude Code, Codex and others) that review, run or extend this repo.

## What this repo is
An evidence-first test of one hypothesis: **"cross-chain volume through NEAR Intents is a better leading indicator
of real NEAR network usage than the NEAR token price."** The result can be SUPPORTED, REJECTED, NOT SUPPORTED or
MIXED, decided by a rule coded in `pipeline/hypothesis.py` before any results were seen. A separate appendix
(`docs/valuation.html`, `pipeline/build.py` + `valuation.py`) checks NEAR's valuation against its own history.

## Verify it in about 2 minutes
```bash
pip install -r requirements.txt
python run.py --offline                       # rebuild from committed data/raw/, no keys, no network
python -m unittest discover -s tests -v       # all tests should pass
python -m http.server -d docs 8000            # open http://localhost:8000
```
Expected output includes `thesis: ... weeks -> hypothesis <RESULT>`. The result and every number in `THESIS.md`
must match `reports/thesis_results.md` at the snapshot date stated at the top of `THESIS.md`.

## Layout
| Path | Role | Edit by hand? |
|---|---|---|
| `sql/*.sql` | BigQuery queries; every one filters on `block_date` | yes |
| `pipeline/bq.py` | Runs `sql/`, dry-run cost guard (`BQ_MAX_GB`), incremental cache | yes |
| `pipeline/intents.py` | Explorer API hour sampler: 1 request / 5 s, resumable | yes |
| `pipeline/hypothesis.py` | Weekly growth, lead-lag, F-test, out-of-sample, **verdict rule** | only with a stated reason; the rule is pre-registered |
| `pipeline/thesis.py` | Charts (data + query + computed sentence) and report | yes |
| `data/raw/intents_hour_samples.csv` | Append-only sample cache | **never rewrite or edit rows** |
| `data/raw/bq_*.csv` | BigQuery results cache | **no**, regenerate with `run.py` |
| `data/processed/`, `docs/data/`, `reports/` | Generated | **no** |
| `THESIS.md` | Human-written conclusion pinned to a snapshot date | yes, keep the numbers in sync |

## Invariants: don't break these
- **Never invent numbers.** Sentences on the dashboard are computed from data in `pipeline/thesis.py`. A metric whose
  source is unavailable is shown as "Not computed", never estimated or filled in.
- **No secrets in the repo.** `NEAR_INTENTS_JWT` and the GCP key come from the environment or `.env`, which is git-ignored.
- **BigQuery cost:** every query keeps its `block_date` filter and passes the dry-run cap.
- **Explorer rate limit:** keep `MIN_GAP` ≥ 5 s. If the API changes and a page repeats, the sampler must stop with an
  error, never loop. (A known quirk: sending an empty `lastDepositMemo` repeats the page.)
- **Label sources.** If BigQuery is stale, usage comes from NearBlocks and the target names say so. Don't join
  BigQuery and NearBlocks into one series; their definitions differ.
- **No look-ahead** in the out-of-sample test: each forecast uses only earlier weeks.

## Reviewer checklist
- [ ] `python run.py --offline` succeeds and prints the hypothesis result.
- [ ] Tests pass, including `HypothesisTest.test_detects_a_real_lead` and `test_does_not_invent_a_lead`.
- [ ] The dashboard loads with no console errors. Every chart has a "Query behind this chart" panel and one sentence.
- [ ] `THESIS.md` lists evidence for, evidence against, what would change the author's mind, and what can't be computed.
