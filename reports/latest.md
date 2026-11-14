# NEAR valuation check - latest numbers

_Generated automatically by `python run.py`. Data as of **2026-11-13** (fetched 2026-11-14T03:05:01Z). Do not edit by hand: the next pipeline run overwrites this file._

## Verdict: **Overvalued**

| Check | Reading | Signal |
|---|---:|---|
| 1. Fair value (NEAR's median multiples over 2 years) | market cap $4.48B vs fair value $2.50B (band $1.88B - $5.31B), +79.3% vs midpoint | fair |
| 2. Confidence Premium (valuation - fundamentals percentile) | +30.7 | overvalued |
| 3. Multiples vs own 2-year history (median rank, 0-100) | 76 | overvalued |

Price $3.42; price implied by fair value midpoint $1.91. Verdict = majority of the three checks (Mixed if no two agree).

| Multiple | Today | 2-year median | Rank (0-100) | Fair value at median |
|---|---:|---:|---:|---:|
| Market cap / revenue (fees burned, annualised) | 4,067.3x | 1,529.1x | 76 | $1.69B |
| Market cap / DEX volume (annualised) | 0.09x | 0.10x | 49 | $4.52B |
| Market cap / TVL | 22.3x | 20.4x | 67 | $4.11B |
| Market cap / stablecoin supply | 34.7x | 15.1x | 92 | $1.95B |
| Market cap per returning account | $81.01K | $28.96K | 84 | $1.60B |

90-day forward price change by fair-value position (descriptive, overlapping windows):

| After | Days | Median | Mean | Share positive |
|---|---:|---:|---:|---:|
| market cap below band | 62 | -0.5% | +17.8% | 48.4% |
| market cap inside band | 555 | -10.5% | +7.4% | 39.8% |
| market cap above band | 19 | -56.0% | -53.3% | 0.0% |

## Indices (0-100, percentile vs the chain's own trailing 365 days)

| | NEAR | AVAX |
|---|---:|---:|
| Network pillar | 50.1 | 26.0 |
| DeFi pillar | 79.4 | 22.4 |
| Tokenomics pillar | 36.5 | 12.9 |
| **Fundamentals Index** | 55.3 | 20.4 |
| **Valuation Index** | 86.0 | 30.8 |
| **Confidence Premium** (Valuation - Fundamentals) | 30.7 | 10.3 |

- NEAR: valuation runs ahead of fundamentals (confidence premium).
- AVAX: valuation roughly in line with fundamentals.

### Robustness (2000 random weightings of pillars and metrics)

| | median | 5th pct | 95th pct | share of draws < 0 |
|---|---:|---:|---:|---:|
| NEAR premium | 31.6 | 13.1 | 44.2 | 0% |
| AVAX premium | 10.9 | 1.7 | 16.8 | 3% |
| NEAR minus AVAX | 21.5 | 3.6 | 33.1 | 3% |

### Does the premium predict returns? (90-day forward price change, descriptive)

| Chain | Bucket | Days | Median | Mean | Share positive |
|---|---|---:|---:|---:|---:|
| NEAR | premium <= -15 | 255 | -6.6% | +8.9% | 44.3% |
| NEAR | -15 < premium < +15 | 361 | -9.8% | -2.9% | 36.6% |
| NEAR | premium >= +15 | 221 | -19.0% | +13.1% | 44.8% |
| AVAX | premium <= -15 | 580 | -4.1% | +1.6% | 44.3% |
| AVAX | -15 < premium < +15 | 159 | -36.1% | -29.2% | 15.7% |
| AVAX | premium >= +15 | 35 | -43.4% | -47.4% | 0.0% |

Overlapping windows over a single two-year regime: read this as a description, not a trading signal.

## Appendix: NEAR vs AVAX snapshot (trailing 30 days)

| Metric | NEAR | AVAX | NEAR / AVAX |
|---|---:|---:|---:|
| Price | $3.42 | $8.38 | 0.41 |
| Market cap | $4.48B | $3.74B | 1.20 |
| Fully diluted value | $4.48B | $3.95B | 1.14 |
| Fees, annualised (30d) | $1.58M | $4.23M | 0.37 |
| Revenue = fees burned, annualised (30d) | $1.10M | $4.23M | 0.26 |
| DeFi TVL | $159.15M | $602.49M | 0.26 |
| DEX volume, annualised (30d) | $47.36B | $30.42B | 1.56 |
| Stablecoin supply | $132.03M | $901.01M | 0.15 |
| Active accounts / day (30d avg) | 64,822 | 65,005 | 1.00 |
| Returning share of active (30d) | 83.7% | 67.2% | 1.25 |
| Transactions / day (30d avg) | 678,139 | 300,639 | 2.26 |
| Staked share of circulating | 47.1% | 45.6% | 1.03 |
| Net supply growth, last 365d | +2.5% | n/a |  |
| Net supply growth, annualised (last 30d) | +2.5% | +8.6% |  |
| Gross issuance offset by burn (30d) | 0.8% | 1.3% | 0.60 |
| **Market cap / revenue** | 4,067.3x | 884.3x | 4.60 |
| Market cap / fees | 2,847.1x | 884.3x | 3.22 |
| Market cap / TVL | 28.2x | 6.21x | 4.54 |
| FDV / TVL | 28.2x | 6.56x | 4.30 |
| Market cap / DEX volume | 0.09x | 0.12x | 0.77 |
| Market cap / stablecoins | 34.0x | 4.15x | 8.18 |
| Market cap per active account | $69.18K | $57.55K | 1.20 |
| Revenue per active account (annual) | $17.01 | $65.08 | 0.26 |
| YoY active accounts | -75.2% | -70.7% |  |
| YoY transactions | -84.5% | -86.1% |  |
| YoY fees | -42.7% | -52.6% |  |
| YoY TVL | +36.7% | -66.7% |  |
| YoY DEX volume | +7.3% | -70.9% |  |
| YoY stablecoins | -39.6% | -50.3% |  |
| YoY market cap | +94.7% | -51.2% |  |

Notes: AVAX figures are the C-chain (Avalanche L1s excluded). Active accounts = daily distinct signers (NEAR: NearBlocks; AVAX: `activeSenders`). Revenue = fees burned: 70% of NEAR fees (30% go to contract developers), 100% of AVAX C-chain fees. AVAX FDV uses today's total supply. NEAR staking history is collected one snapshot per run (2 so far), so NEAR's staking score starts once enough snapshots accrue.
