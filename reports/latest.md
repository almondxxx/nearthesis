# NEAR valuation check - latest numbers

_Generated automatically by `python run.py`. Data as of **2026-11-19** (fetched 2026-11-20T03:02:32Z). Do not edit by hand: the next pipeline run overwrites this file._

## Verdict: **Overvalued**

| Check | Reading | Signal |
|---|---:|---|
| 1. Fair value (NEAR's median multiples over 2 years) | market cap $4.33B vs fair value $2.44B (band $1.84B - $5.19B), +77.6% vs midpoint | fair |
| 2. Confidence Premium (valuation - fundamentals percentile) | +33.6 | overvalued |
| 3. Multiples vs own 2-year history (median rank, 0-100) | 78 | overvalued |

Price $3.30; price implied by fair value midpoint $1.86. Verdict = majority of the three checks (Mixed if no two agree).

| Multiple | Today | 2-year median | Rank (0-100) | Fair value at median |
|---|---:|---:|---:|---:|
| Market cap / revenue (fees burned, annualised) | 4,753.1x | 1,538.0x | 78 | $1.40B |
| Market cap / DEX volume (annualised) | 0.09x | 0.09x | 45 | $4.65B |
| Market cap / TVL | 23.3x | 20.4x | 75 | $3.79B |
| Market cap / stablecoin supply | 33.3x | 15.1x | 92 | $1.97B |
| Market cap per returning account | $71.48K | $29.21K | 79 | $1.77B |

90-day forward price change by fair-value position (descriptive, overlapping windows):

| After | Days | Median | Mean | Share positive |
|---|---:|---:|---:|---:|
| market cap below band | 62 | -0.5% | +17.8% | 48.4% |
| market cap inside band | 561 | -10.0% | +8.3% | 40.5% |
| market cap above band | 19 | -56.0% | -53.3% | 0.0% |

## Indices (0-100, percentile vs the chain's own trailing 365 days)

| | NEAR | AVAX |
|---|---:|---:|
| Network pillar | 37.0 | 26.7 |
| DeFi pillar | 80.0 | 15.9 |
| Tokenomics pillar | 34.5 | 10.4 |
| **Fundamentals Index** | 50.5 | 17.7 |
| **Valuation Index** | 84.1 | 26.1 |
| **Confidence Premium** (Valuation - Fundamentals) | 33.6 | 8.4 |

- NEAR: valuation runs ahead of fundamentals (confidence premium).
- AVAX: valuation roughly in line with fundamentals.

### Robustness (2000 random weightings of pillars and metrics)

| | median | 5th pct | 95th pct | share of draws < 0 |
|---|---:|---:|---:|---:|
| NEAR premium | 35.4 | 12.9 | 48.1 | 0% |
| AVAX premium | 9.3 | -1.2 | 14.4 | 7% |
| NEAR minus AVAX | 26.4 | 3.0 | 43.3 | 3% |

### Does the premium predict returns? (90-day forward price change, descriptive)

| Chain | Bucket | Days | Median | Mean | Share positive |
|---|---|---:|---:|---:|---:|
| NEAR | premium <= -15 | 255 | -6.6% | +8.9% | 44.3% |
| NEAR | -15 < premium < +15 | 367 | -9.2% | -1.3% | 37.6% |
| NEAR | premium >= +15 | 221 | -19.0% | +13.1% | 44.8% |
| AVAX | premium <= -15 | 583 | -3.9% | +1.6% | 44.6% |
| AVAX | -15 < premium < +15 | 160 | -35.5% | -28.1% | 16.9% |
| AVAX | premium >= +15 | 37 | -42.6% | -46.9% | 0.0% |

Overlapping windows over a single two-year regime: read this as a description, not a trading signal.

## Appendix: NEAR vs AVAX snapshot (trailing 30 days)

| Metric | NEAR | AVAX | NEAR / AVAX |
|---|---:|---:|---:|
| Price | $3.30 | $7.01 | 0.47 |
| Market cap | $4.33B | $3.13B | 1.38 |
| Fully diluted value | $4.33B | $3.31B | 1.31 |
| Fees, annualised (30d) | $1.21M | $4.40M | 0.28 |
| Revenue = fees burned, annualised (30d) | $911.11K | $4.40M | 0.21 |
| DeFi TVL | $153.76M | $542.86M | 0.28 |
| DEX volume, annualised (30d) | $49.11B | $27.48B | 1.79 |
| Stablecoin supply | $132.52M | $787.74M | 0.17 |
| Active accounts / day (30d avg) | 69,666 | 64,783 | 1.08 |
| Returning share of active (30d) | 85.2% | 66.4% | 1.28 |
| Transactions / day (30d avg) | 685,545 | 318,895 | 2.15 |
| Staked share of circulating | 47.7% | 45.5% | 1.05 |
| Net supply growth, last 365d | +2.5% | n/a |  |
| Net supply growth, annualised (last 30d) | +2.5% | +8.6% |  |
| Gross issuance offset by burn (30d) | 0.7% | 1.4% | 0.50 |
| **Market cap / revenue** | 4,753.1x | 711.9x | 6.68 |
| Market cap / fees | 3,568.3x | 711.9x | 5.01 |
| Market cap / TVL | 28.2x | 5.77x | 4.88 |
| FDV / TVL | 28.2x | 6.09x | 4.62 |
| Market cap / DEX volume | 0.09x | 0.11x | 0.77 |
| Market cap / stablecoins | 32.7x | 3.97x | 8.22 |
| Market cap per active account | $62.16K | $48.32K | 1.29 |
| Revenue per active account (annual) | $13.08 | $67.88 | 0.19 |
| YoY active accounts | -72.7% | -72.8% |  |
| YoY transactions | -84.2% | -85.1% |  |
| YoY fees | -56.1% | -45.8% |  |
| YoY TVL | +22.2% | -65.0% |  |
| YoY DEX volume | -5.4% | -72.2% |  |
| YoY stablecoins | -35.0% | -51.1% |  |
| YoY market cap | +77.1% | -50.9% |  |

Notes: AVAX figures are the C-chain (Avalanche L1s excluded). Active accounts = daily distinct signers (NEAR: NearBlocks; AVAX: `activeSenders`). Revenue = fees burned: 70% of NEAR fees (30% go to contract developers), 100% of AVAX C-chain fees. AVAX FDV uses today's total supply. NEAR staking history is collected one snapshot per run (8 so far), so NEAR's staking score starts once enough snapshots accrue.
