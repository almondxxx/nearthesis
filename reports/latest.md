# NEAR valuation check - latest numbers

_Generated automatically by `python run.py`. Data as of **2026-11-20** (fetched 2026-11-21T03:03:04Z). Do not edit by hand: the next pipeline run overwrites this file._

## Verdict: **Overvalued**

| Check | Reading | Signal |
|---|---:|---|
| 1. Fair value (NEAR's median multiples over 2 years) | market cap $4.21B vs fair value $2.43B (band $1.83B - $5.17B), +73.0% vs midpoint | fair |
| 2. Confidence Premium (valuation - fundamentals percentile) | +39.0 | overvalued |
| 3. Multiples vs own 2-year history (median rank, 0-100) | 77 | overvalued |

Price $3.21; price implied by fair value midpoint $1.85. Verdict = majority of the three checks (Mixed if no two agree).

| Multiple | Today | 2-year median | Rank (0-100) | Fair value at median |
|---|---:|---:|---:|---:|
| Market cap / revenue (fees burned, annualised) | 4,657.3x | 1,543.5x | 77 | $1.39B |
| Market cap / DEX volume (annualised) | 0.09x | 0.09x | 44 | $4.61B |
| Market cap / TVL | 22.9x | 20.4x | 73 | $3.74B |
| Market cap / stablecoin supply | 32.3x | 15.1x | 92 | $1.97B |
| Market cap per returning account | $68.61K | $29.23K | 78 | $1.79B |

90-day forward price change by fair-value position (descriptive, overlapping windows):

| After | Days | Median | Mean | Share positive |
|---|---:|---:|---:|---:|
| market cap below band | 62 | -0.5% | +17.8% | 48.4% |
| market cap inside band | 562 | -9.9% | +8.4% | 40.6% |
| market cap above band | 19 | -56.0% | -53.3% | 0.0% |

## Indices (0-100, percentile vs the chain's own trailing 365 days)

| | NEAR | AVAX |
|---|---:|---:|
| Network pillar | 33.9 | 27.0 |
| DeFi pillar | 78.6 | 15.2 |
| Tokenomics pillar | 21.8 | 11.2 |
| **Fundamentals Index** | 44.8 | 17.8 |
| **Valuation Index** | 83.8 | 23.9 |
| **Confidence Premium** (Valuation - Fundamentals) | 39.0 | 6.1 |

- NEAR: valuation runs ahead of fundamentals (confidence premium).
- AVAX: valuation roughly in line with fundamentals.

### Robustness (2000 random weightings of pillars and metrics)

| | median | 5th pct | 95th pct | share of draws < 0 |
|---|---:|---:|---:|---:|
| NEAR premium | 40.8 | 14.7 | 56.5 | 0% |
| AVAX premium | 7.1 | -3.3 | 11.8 | 11% |
| NEAR minus AVAX | 35.1 | 7.3 | 51.3 | 1% |

### Does the premium predict returns? (90-day forward price change, descriptive)

| Chain | Bucket | Days | Median | Mean | Share positive |
|---|---|---:|---:|---:|---:|
| NEAR | premium <= -15 | 255 | -6.6% | +8.9% | 44.3% |
| NEAR | -15 < premium < +15 | 367 | -9.2% | -1.3% | 37.6% |
| NEAR | premium >= +15 | 222 | -18.7% | +13.3% | 45.0% |
| AVAX | premium <= -15 | 583 | -3.9% | +1.6% | 44.6% |
| AVAX | -15 < premium < +15 | 161 | -35.2% | -28.0% | 16.8% |
| AVAX | premium >= +15 | 37 | -42.6% | -46.9% | 0.0% |

Overlapping windows over a single two-year regime: read this as a description, not a trading signal.

## Appendix: NEAR vs AVAX snapshot (trailing 30 days)

| Metric | NEAR | AVAX | NEAR / AVAX |
|---|---:|---:|---:|
| Price | $3.21 | $6.89 | 0.47 |
| Market cap | $4.21B | $3.08B | 1.37 |
| Fully diluted value | $4.21B | $3.25B | 1.30 |
| Fees, annualised (30d) | $1.19M | $4.47M | 0.27 |
| Revenue = fees burned, annualised (30d) | $903.10K | $4.47M | 0.20 |
| DeFi TVL | $150.92M | $546.54M | 0.28 |
| DEX volume, annualised (30d) | $48.72B | $26.96B | 1.81 |
| Stablecoin supply | $133.23M | $894.34M | 0.15 |
| Active accounts / day (30d avg) | 70,302 | 65,008 | 1.08 |
| Returning share of active (30d) | 85.5% | 66.2% | 1.29 |
| Transactions / day (30d avg) | 689,538 | 320,822 | 2.15 |
| Staked share of circulating | 47.7% | 45.5% | 1.05 |
| Net supply growth, last 365d | +2.5% | n/a |  |
| Net supply growth, annualised (last 30d) | +2.5% | +7.8% |  |
| Gross issuance offset by burn (30d) | 0.7% | 1.5% | 0.47 |
| **Market cap / revenue** | 4,657.3x | 688.5x | 6.76 |
| Market cap / fees | 3,545.3x | 688.5x | 5.15 |
| Market cap / TVL | 27.9x | 5.63x | 4.95 |
| FDV / TVL | 27.9x | 5.94x | 4.69 |
| Market cap / DEX volume | 0.09x | 0.11x | 0.76 |
| Market cap / stablecoins | 31.6x | 3.44x | 9.18 |
| Market cap per active account | $59.83K | $47.31K | 1.26 |
| Revenue per active account (annual) | $12.85 | $68.72 | 0.19 |
| YoY active accounts | -72.4% | -73.4% |  |
| YoY transactions | -84.1% | -85.1% |  |
| YoY fees | -57.0% | -45.3% |  |
| YoY TVL | +20.0% | -64.6% |  |
| YoY DEX volume | -9.3% | -73.5% |  |
| YoY stablecoins | -34.3% | -51.1% |  |
| YoY market cap | +74.2% | -50.9% |  |

Notes: AVAX figures are the C-chain (Avalanche L1s excluded). Active accounts = daily distinct signers (NEAR: NearBlocks; AVAX: `activeSenders`). Revenue = fees burned: 70% of NEAR fees (30% go to contract developers), 100% of AVAX C-chain fees. AVAX FDV uses today's total supply. NEAR staking history is collected one snapshot per run (9 so far), so NEAR's staking score starts once enough snapshots accrue.
