# NEAR valuation check - latest numbers

_Generated automatically by `python run.py`. Data as of **2026-11-18** (fetched 2026-11-19T03:08:43Z). Do not edit by hand: the next pipeline run overwrites this file._

## Verdict: **Overvalued**

| Check | Reading | Signal |
|---|---:|---|
| 1. Fair value (NEAR's median multiples over 2 years) | market cap $4.45B vs fair value $2.44B (band $1.83B - $5.19B), +82.6% vs midpoint | fair |
| 2. Confidence Premium (valuation - fundamentals percentile) | +32.5 | overvalued |
| 3. Multiples vs own 2-year history (median rank, 0-100) | 79 | overvalued |

Price $3.39; price implied by fair value midpoint $1.86. Verdict = majority of the three checks (Mixed if no two agree).

| Multiple | Today | 2-year median | Rank (0-100) | Fair value at median |
|---|---:|---:|---:|---:|
| Market cap / revenue (fees burned, annualised) | 4,869.9x | 1,538.0x | 79 | $1.41B |
| Market cap / DEX volume (annualised) | 0.09x | 0.09x | 46 | $4.66B |
| Market cap / TVL | 23.6x | 20.4x | 76 | $3.84B |
| Market cap / stablecoin supply | 34.2x | 15.1x | 92 | $1.96B |
| Market cap per returning account | $74.62K | $29.17K | 82 | $1.74B |

90-day forward price change by fair-value position (descriptive, overlapping windows):

| After | Days | Median | Mean | Share positive |
|---|---:|---:|---:|---:|
| market cap below band | 62 | -0.5% | +17.8% | 48.4% |
| market cap inside band | 560 | -10.1% | +8.2% | 40.4% |
| market cap above band | 19 | -56.0% | -53.3% | 0.0% |

## Indices (0-100, percentile vs the chain's own trailing 365 days)

| | NEAR | AVAX |
|---|---:|---:|
| Network pillar | 40.6 | 26.7 |
| DeFi pillar | 81.4 | 17.1 |
| Tokenomics pillar | 33.5 | 10.5 |
| **Fundamentals Index** | 51.8 | 18.1 |
| **Valuation Index** | 84.3 | 28.8 |
| **Confidence Premium** (Valuation - Fundamentals) | 32.5 | 10.7 |

- NEAR: valuation runs ahead of fundamentals (confidence premium).
- AVAX: valuation roughly in line with fundamentals.

### Robustness (2000 random weightings of pillars and metrics)

| | median | 5th pct | 95th pct | share of draws < 0 |
|---|---:|---:|---:|---:|
| NEAR premium | 34.3 | 11.7 | 47.3 | 0% |
| AVAX premium | 11.5 | 1.0 | 16.9 | 4% |
| NEAR minus AVAX | 23.2 | -0.0 | 39.0 | 5% |

### Does the premium predict returns? (90-day forward price change, descriptive)

| Chain | Bucket | Days | Median | Mean | Share positive |
|---|---|---:|---:|---:|---:|
| NEAR | premium <= -15 | 255 | -6.6% | +8.9% | 44.3% |
| NEAR | -15 < premium < +15 | 366 | -9.2% | -1.5% | 37.4% |
| NEAR | premium >= +15 | 221 | -19.0% | +13.1% | 44.8% |
| AVAX | premium <= -15 | 582 | -3.9% | +1.6% | 44.7% |
| AVAX | -15 < premium < +15 | 160 | -35.5% | -28.1% | 16.9% |
| AVAX | premium >= +15 | 37 | -42.6% | -46.9% | 0.0% |

Overlapping windows over a single two-year regime: read this as a description, not a trading signal.

## Appendix: NEAR vs AVAX snapshot (trailing 30 days)

| Metric | NEAR | AVAX | NEAR / AVAX |
|---|---:|---:|---:|
| Price | $3.39 | $7.16 | 0.47 |
| Market cap | $4.45B | $3.20B | 1.39 |
| Fully diluted value | $4.45B | $3.38B | 1.32 |
| Fees, annualised (30d) | $1.23M | $4.42M | 0.28 |
| Revenue = fees burned, annualised (30d) | $913.89K | $4.42M | 0.21 |
| DeFi TVL | $157.74M | $549.89M | 0.29 |
| DEX volume, annualised (30d) | $49.18B | $28.19B | 1.74 |
| Stablecoin supply | $132.89M | $782.42M | 0.17 |
| Active accounts / day (30d avg) | 68,864 | 64,079 | 1.07 |
| Returning share of active (30d) | 84.8% | 66.4% | 1.28 |
| Transactions / day (30d avg) | 685,330 | 316,664 | 2.16 |
| Staked share of circulating | 47.4% | 45.5% | 1.04 |
| Net supply growth, last 365d | +2.5% | n/a |  |
| Net supply growth, annualised (last 30d) | +2.5% | +8.6% |  |
| Gross issuance offset by burn (30d) | 0.7% | 1.4% | 0.49 |
| **Market cap / revenue** | 4,869.9x | 723.3x | 6.73 |
| Market cap / fees | 3,613.8x | 723.3x | 5.00 |
| Market cap / TVL | 28.2x | 5.82x | 4.85 |
| FDV / TVL | 28.2x | 6.14x | 4.59 |
| Market cap / DEX volume | 0.09x | 0.11x | 0.80 |
| Market cap / stablecoins | 33.5x | 4.09x | 8.19 |
| Market cap per active account | $64.63K | $49.93K | 1.29 |
| Revenue per active account (annual) | $13.27 | $69.04 | 0.19 |
| YoY active accounts | -73.1% | -72.8% |  |
| YoY transactions | -84.3% | -85.2% |  |
| YoY fees | -55.5% | -46.0% |  |
| YoY TVL | +24.4% | -65.3% |  |
| YoY DEX volume | -3.2% | -71.6% |  |
| YoY stablecoins | -35.7% | -51.0% |  |
| YoY market cap | +79.7% | -51.0% |  |

Notes: AVAX figures are the C-chain (Avalanche L1s excluded). Active accounts = daily distinct signers (NEAR: NearBlocks; AVAX: `activeSenders`). Revenue = fees burned: 70% of NEAR fees (30% go to contract developers), 100% of AVAX C-chain fees. AVAX FDV uses today's total supply. NEAR staking history is collected one snapshot per run (7 so far), so NEAR's staking score starts once enough snapshots accrue.
