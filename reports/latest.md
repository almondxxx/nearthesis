# NEAR valuation check - latest numbers

_Generated automatically by `python run.py`. Data as of **2026-11-16** (fetched 2026-11-17T03:05:05Z). Do not edit by hand: the next pipeline run overwrites this file._

## Verdict: **Overvalued**

| Check | Reading | Signal |
|---|---:|---|
| 1. Fair value (NEAR's median multiples over 2 years) | market cap $4.22B vs fair value $2.43B (band $1.83B - $5.20B), +73.5% vs midpoint | fair |
| 2. Confidence Premium (valuation - fundamentals percentile) | +30.4 | overvalued |
| 3. Multiples vs own 2-year history (median rank, 0-100) | 77 | overvalued |

Price $3.21; price implied by fair value midpoint $1.85. Verdict = majority of the three checks (Mixed if no two agree).

| Multiple | Today | 2-year median | Rank (0-100) | Fair value at median |
|---|---:|---:|---:|---:|
| Market cap / revenue (fees burned, annualised) | 4,627.1x | 1,533.7x | 77 | $1.40B |
| Market cap / DEX volume (annualised) | 0.09x | 0.10x | 43 | $4.68B |
| Market cap / TVL | 21.8x | 20.4x | 63 | $3.94B |
| Market cap / stablecoin supply | 32.5x | 15.1x | 92 | $1.96B |
| Market cap per returning account | $72.93K | $29.07K | 80 | $1.68B |

90-day forward price change by fair-value position (descriptive, overlapping windows):

| After | Days | Median | Mean | Share positive |
|---|---:|---:|---:|---:|
| market cap below band | 62 | -0.5% | +17.8% | 48.4% |
| market cap inside band | 558 | -10.3% | +7.9% | 40.1% |
| market cap above band | 19 | -56.0% | -53.3% | 0.0% |

## Indices (0-100, percentile vs the chain's own trailing 365 days)

| | NEAR | AVAX |
|---|---:|---:|
| Network pillar | 50.8 | 26.7 |
| DeFi pillar | 81.2 | 21.9 |
| Tokenomics pillar | 32.3 | 10.6 |
| **Fundamentals Index** | 54.8 | 19.7 |
| **Valuation Index** | 85.2 | 29.4 |
| **Confidence Premium** (Valuation - Fundamentals) | 30.4 | 9.7 |

- NEAR: valuation runs ahead of fundamentals (confidence premium).
- AVAX: valuation roughly in line with fundamentals.

### Robustness (2000 random weightings of pillars and metrics)

| | median | 5th pct | 95th pct | share of draws < 0 |
|---|---:|---:|---:|---:|
| NEAR premium | 31.3 | 11.6 | 46.2 | 0% |
| AVAX premium | 10.3 | 0.2 | 16.7 | 5% |
| NEAR minus AVAX | 22.0 | 2.9 | 34.4 | 3% |

### Does the premium predict returns? (90-day forward price change, descriptive)

| Chain | Bucket | Days | Median | Mean | Share positive |
|---|---|---:|---:|---:|---:|
| NEAR | premium <= -15 | 255 | -6.6% | +8.9% | 44.3% |
| NEAR | -15 < premium < +15 | 364 | -9.6% | -2.1% | 37.1% |
| NEAR | premium >= +15 | 221 | -19.0% | +13.1% | 44.8% |
| AVAX | premium <= -15 | 582 | -4.0% | +1.6% | 44.5% |
| AVAX | -15 < premium < +15 | 158 | -35.9% | -28.5% | 16.5% |
| AVAX | premium >= +15 | 37 | -42.6% | -46.9% | 0.0% |

Overlapping windows over a single two-year regime: read this as a description, not a trading signal.

## Appendix: NEAR vs AVAX snapshot (trailing 30 days)

| Metric | NEAR | AVAX | NEAR / AVAX |
|---|---:|---:|---:|
| Price | $3.21 | $7.16 | 0.45 |
| Market cap | $4.22B | $3.20B | 1.32 |
| Fully diluted value | $4.22B | $3.38B | 1.25 |
| Fees, annualised (30d) | $1.26M | $4.43M | 0.28 |
| Revenue = fees burned, annualised (30d) | $911.37K | $4.43M | 0.21 |
| DeFi TVL | $149.39M | $547.94M | 0.27 |
| DEX volume, annualised (30d) | $49.08B | $29.09B | 1.69 |
| Stablecoin supply | $132.23M | $811.32M | 0.16 |
| Active accounts / day (30d avg) | 67,141 | 64,151 | 1.05 |
| Returning share of active (30d) | 84.3% | 66.5% | 1.27 |
| Transactions / day (30d avg) | 681,819 | 311,607 | 2.19 |
| Staked share of circulating | 47.3% | 45.5% | 1.04 |
| Net supply growth, last 365d | +2.5% | n/a |  |
| Net supply growth, annualised (last 30d) | +2.5% | +8.2% |  |
| Gross issuance offset by burn (30d) | 0.7% | 1.5% | 0.46 |
| **Market cap / revenue** | 4,627.1x | 721.5x | 6.41 |
| Market cap / fees | 3,354.2x | 721.5x | 4.65 |
| Market cap / TVL | 28.2x | 5.83x | 4.84 |
| FDV / TVL | 28.2x | 6.16x | 4.58 |
| Market cap / DEX volume | 0.09x | 0.11x | 0.78 |
| Market cap / stablecoins | 31.9x | 3.94x | 8.09 |
| Market cap per active account | $62.81K | $49.83K | 1.26 |
| Revenue per active account (annual) | $13.57 | $69.07 | 0.20 |
| YoY active accounts | -74.0% | -72.4% |  |
| YoY transactions | -84.3% | -85.8% |  |
| YoY fees | -54.4% | -44.0% |  |
| YoY TVL | +29.1% | -65.9% |  |
| YoY DEX volume | +2.8% | -70.2% |  |
| YoY stablecoins | -37.0% | -50.7% |  |
| YoY market cap | +85.4% | -50.9% |  |

Notes: AVAX figures are the C-chain (Avalanche L1s excluded). Active accounts = daily distinct signers (NEAR: NearBlocks; AVAX: `activeSenders`). Revenue = fees burned: 70% of NEAR fees (30% go to contract developers), 100% of AVAX C-chain fees. AVAX FDV uses today's total supply. NEAR staking history is collected one snapshot per run (5 so far), so NEAR's staking score starts once enough snapshots accrue.
