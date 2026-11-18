# NEAR valuation check - latest numbers

_Generated automatically by `python run.py`. Data as of **2026-11-17** (fetched 2026-11-18T03:07:49Z). Do not edit by hand: the next pipeline run overwrites this file._

## Verdict: **Overvalued**

| Check | Reading | Signal |
|---|---:|---|
| 1. Fair value (NEAR's median multiples over 2 years) | market cap $4.14B vs fair value $2.43B (band $1.83B - $5.20B), +70.4% vs midpoint | fair |
| 2. Confidence Premium (valuation - fundamentals percentile) | +32.8 | overvalued |
| 3. Multiples vs own 2-year history (median rank, 0-100) | 76 | overvalued |

Price $3.16; price implied by fair value midpoint $1.85. Verdict = majority of the three checks (Mixed if no two agree).

| Multiple | Today | 2-year median | Rank (0-100) | Fair value at median |
|---|---:|---:|---:|---:|
| Market cap / revenue (fees burned, annualised) | 4,534.6x | 1,533.7x | 76 | $1.40B |
| Market cap / DEX volume (annualised) | 0.08x | 0.10x | 43 | $4.65B |
| Market cap / TVL | 21.7x | 20.4x | 62 | $3.89B |
| Market cap / stablecoin supply | 31.9x | 15.1x | 92 | $1.96B |
| Market cap per returning account | $70.48K | $29.12K | 79 | $1.71B |

90-day forward price change by fair-value position (descriptive, overlapping windows):

| After | Days | Median | Mean | Share positive |
|---|---:|---:|---:|---:|
| market cap below band | 62 | -0.5% | +17.8% | 48.4% |
| market cap inside band | 559 | -10.2% | +8.1% | 40.3% |
| market cap above band | 19 | -56.0% | -53.3% | 0.0% |

## Indices (0-100, percentile vs the chain's own trailing 365 days)

| | NEAR | AVAX |
|---|---:|---:|
| Network pillar | 43.4 | 26.9 |
| DeFi pillar | 80.2 | 20.1 |
| Tokenomics pillar | 32.6 | 10.5 |
| **Fundamentals Index** | 52.1 | 19.1 |
| **Valuation Index** | 84.9 | 28.8 |
| **Confidence Premium** (Valuation - Fundamentals) | 32.8 | 9.7 |

- NEAR: valuation runs ahead of fundamentals (confidence premium).
- AVAX: valuation roughly in line with fundamentals.

### Robustness (2000 random weightings of pillars and metrics)

| | median | 5th pct | 95th pct | share of draws < 0 |
|---|---:|---:|---:|---:|
| NEAR premium | 34.3 | 12.5 | 47.7 | 0% |
| AVAX premium | 10.5 | 0.2 | 16.4 | 5% |
| NEAR minus AVAX | 24.6 | 3.6 | 38.5 | 3% |

### Does the premium predict returns? (90-day forward price change, descriptive)

| Chain | Bucket | Days | Median | Mean | Share positive |
|---|---|---:|---:|---:|---:|
| NEAR | premium <= -15 | 255 | -6.6% | +8.9% | 44.3% |
| NEAR | -15 < premium < +15 | 365 | -9.3% | -1.8% | 37.3% |
| NEAR | premium >= +15 | 221 | -19.0% | +13.1% | 44.8% |
| AVAX | premium <= -15 | 583 | -4.0% | +1.6% | 44.6% |
| AVAX | -15 < premium < +15 | 158 | -35.9% | -28.5% | 16.5% |
| AVAX | premium >= +15 | 37 | -42.6% | -46.9% | 0.0% |

Overlapping windows over a single two-year regime: read this as a description, not a trading signal.

## Appendix: NEAR vs AVAX snapshot (trailing 30 days)

| Metric | NEAR | AVAX | NEAR / AVAX |
|---|---:|---:|---:|
| Price | $3.16 | $7.10 | 0.44 |
| Market cap | $4.14B | $3.17B | 1.31 |
| Fully diluted value | $4.14B | $3.35B | 1.24 |
| Fees, annualised (30d) | $1.25M | $4.44M | 0.28 |
| Revenue = fees burned, annualised (30d) | $913.84K | $4.44M | 0.21 |
| DeFi TVL | $147.63M | $544.36M | 0.27 |
| DEX volume, annualised (30d) | $48.87B | $28.74B | 1.70 |
| Stablecoin supply | $132.35M | $801.00M | 0.17 |
| Active accounts / day (30d avg) | 68,057 | 64,110 | 1.06 |
| Returning share of active (30d) | 84.6% | 66.4% | 1.27 |
| Transactions / day (30d avg) | 684,675 | 314,570 | 2.18 |
| Staked share of circulating | 47.6% | 45.5% | 1.04 |
| Net supply growth, last 365d | +2.5% | n/a |  |
| Net supply growth, annualised (last 30d) | +2.5% | +8.5% |  |
| Gross issuance offset by burn (30d) | 0.7% | 1.4% | 0.48 |
| **Market cap / revenue** | 4,534.6x | 714.7x | 6.34 |
| Market cap / fees | 3,326.0x | 714.7x | 4.65 |
| Market cap / TVL | 28.1x | 5.82x | 4.82 |
| FDV / TVL | 28.1x | 6.15x | 4.56 |
| Market cap / DEX volume | 0.08x | 0.11x | 0.77 |
| Market cap / stablecoins | 31.3x | 3.96x | 7.91 |
| Market cap per active account | $60.89K | $49.44K | 1.23 |
| Revenue per active account (annual) | $13.43 | $69.18 | 0.19 |
| YoY active accounts | -73.6% | -72.2% |  |
| YoY transactions | -84.3% | -85.5% |  |
| YoY fees | -55.0% | -45.2% |  |
| YoY TVL | +26.6% | -65.7% |  |
| YoY DEX volume | -0.7% | -70.9% |  |
| YoY stablecoins | -36.4% | -50.9% |  |
| YoY market cap | +82.4% | -51.0% |  |

Notes: AVAX figures are the C-chain (Avalanche L1s excluded). Active accounts = daily distinct signers (NEAR: NearBlocks; AVAX: `activeSenders`). Revenue = fees burned: 70% of NEAR fees (30% go to contract developers), 100% of AVAX C-chain fees. AVAX FDV uses today's total supply. NEAR staking history is collected one snapshot per run (6 so far), so NEAR's staking score starts once enough snapshots accrue.
