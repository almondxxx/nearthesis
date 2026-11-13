# NEAR valuation check - latest numbers

_Generated automatically by `python run.py`. Data as of **2026-11-12** (fetched 2026-11-13T16:28:16Z). Do not edit by hand: the next pipeline run overwrites this file._

## Verdict: **Overvalued**

| Check | Reading | Signal |
|---|---:|---|
| 1. Fair value (NEAR's median multiples over 2 years) | market cap $4.70B vs fair value $2.52B (band $1.90B - $5.37B), +86.3% vs midpoint | fair |
| 2. Confidence Premium (valuation - fundamentals percentile) | +28.6 | overvalued |
| 3. Multiples vs own 2-year history (median rank, 0-100) | 76 | overvalued |

Price $3.59; price implied by fair value midpoint $1.92. Verdict = majority of the three checks (Mixed if no two agree).

| Multiple | Today | 2-year median | Rank (0-100) | Fair value at median |
|---|---:|---:|---:|---:|
| Market cap / revenue (fees burned, annualised) | 4,201.9x | 1,525.5x | 76 | $1.71B |
| Market cap / DEX volume (annualised) | 0.10x | 0.10x | 50 | $4.71B |
| Market cap / TVL | 23.0x | 20.4x | 73 | $4.17B |
| Market cap / stablecoin supply | 36.4x | 15.0x | 93 | $1.95B |
| Market cap per returning account | $86.56K | $28.93K | 85 | $1.57B |

90-day forward price change by fair-value position (descriptive, overlapping windows):

| After | Days | Median | Mean | Share positive |
|---|---:|---:|---:|---:|
| market cap below band | 62 | -0.5% | +17.8% | 48.4% |
| market cap inside band | 554 | -10.7% | +7.2% | 39.7% |
| market cap above band | 19 | -56.0% | -53.3% | 0.0% |

## Indices (0-100, percentile vs the chain's own trailing 365 days)

| | NEAR | AVAX |
|---|---:|---:|
| Network pillar | 48.1 | 25.5 |
| DeFi pillar | 88.3 | 20.9 |
| Tokenomics pillar | 36.7 | 13.7 |
| **Fundamentals Index** | 57.7 | 20.0 |
| **Valuation Index** | 86.3 | 29.9 |
| **Confidence Premium** (Valuation - Fundamentals) | 28.6 | 9.9 |

- NEAR: valuation runs ahead of fundamentals (confidence premium).
- AVAX: valuation roughly in line with fundamentals.

### Robustness (2000 random weightings of pillars and metrics)

| | median | 5th pct | 95th pct | share of draws < 0 |
|---|---:|---:|---:|---:|
| NEAR premium | 30.0 | 7.3 | 44.3 | 0% |
| AVAX premium | 10.5 | 1.7 | 15.9 | 3% |
| NEAR minus AVAX | 20.3 | -2.5 | 34.5 | 7% |

### Does the premium predict returns? (90-day forward price change, descriptive)

| Chain | Bucket | Days | Median | Mean | Share positive |
|---|---|---:|---:|---:|---:|
| NEAR | premium <= -15 | 255 | -6.6% | +8.9% | 44.3% |
| NEAR | -15 < premium < +15 | 360 | -9.9% | -3.2% | 36.4% |
| NEAR | premium >= +15 | 221 | -19.0% | +13.1% | 44.8% |
| AVAX | premium <= -15 | 579 | -4.1% | +1.6% | 44.2% |
| AVAX | -15 < premium < +15 | 160 | -36.1% | -29.4% | 15.6% |
| AVAX | premium >= +15 | 34 | -43.0% | -47.2% | 0.0% |

Overlapping windows over a single two-year regime: read this as a description, not a trading signal.

## Appendix: NEAR vs AVAX snapshot (trailing 30 days)

| Metric | NEAR | AVAX | NEAR / AVAX |
|---|---:|---:|---:|
| Price | $3.59 | $8.51 | 0.42 |
| Market cap | $4.70B | $3.79B | 1.24 |
| Fully diluted value | $4.70B | $4.01B | 1.17 |
| Fees, annualised (30d) | $1.60M | $4.17M | 0.38 |
| Revenue = fees burned, annualised (30d) | $1.12M | $4.17M | 0.27 |
| DeFi TVL | $167.82M | $608.95M | 0.28 |
| DEX volume, annualised (30d) | $49.26B | $30.50B | 1.61 |
| Stablecoin supply | $131.25M | $909.05M | 0.14 |
| Active accounts / day (30d avg) | 63,923 | 65,396 | 0.98 |
| Returning share of active (30d) | 83.3% | 68.0% | 1.23 |
| Transactions / day (30d avg) | 669,188 | 295,821 | 2.26 |
| Staked share of circulating | 47.2% | 45.6% | 1.03 |
| Net supply growth, last 365d | +2.5% | n/a |  |
| Net supply growth, annualised (last 30d) | +2.5% | +7.1% |  |
| Gross issuance offset by burn (30d) | 0.8% | 1.5% | 0.50 |
| **Market cap / revenue** | 4,201.9x | 909.6x | 4.62 |
| Market cap / fees | 2,941.4x | 909.6x | 3.23 |
| Market cap / TVL | 28.0x | 6.23x | 4.50 |
| FDV / TVL | 28.0x | 6.59x | 4.25 |
| Market cap / DEX volume | 0.10x | 0.12x | 0.77 |
| Market cap / stablecoins | 35.8x | 4.17x | 8.58 |
| Market cap per active account | $73.56K | $58.01K | 1.27 |
| Revenue per active account (annual) | $17.51 | $63.78 | 0.27 |
| YoY active accounts | -75.6% | -70.8% |  |
| YoY transactions | -84.8% | -86.2% |  |
| YoY fees | -42.0% | -55.5% |  |
| YoY TVL | +39.0% | -67.1% |  |
| YoY DEX volume | +14.5% | -72.1% |  |
| YoY stablecoins | -40.6% | -50.5% |  |
| YoY market cap | +97.0% | -51.4% |  |

Notes: AVAX figures are the C-chain (Avalanche L1s excluded). Active accounts = daily distinct signers (NEAR: NearBlocks; AVAX: `activeSenders`). Revenue = fees burned: 70% of NEAR fees (30% go to contract developers), 100% of AVAX C-chain fees. AVAX FDV uses today's total supply. NEAR staking history is collected one snapshot per run (1 so far), so NEAR's staking score starts once enough snapshots accrue.
