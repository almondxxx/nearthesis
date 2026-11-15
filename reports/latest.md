# NEAR valuation check - latest numbers

_Generated automatically by `python run.py`. Data as of **2026-11-14** (fetched 2026-11-15T03:04:33Z). Do not edit by hand: the next pipeline run overwrites this file._

## Verdict: **Overvalued**

| Check | Reading | Signal |
|---|---:|---|
| 1. Fair value (NEAR's median multiples over 2 years) | market cap $4.52B vs fair value $2.42B (band $1.83B - $5.16B), +86.5% vs midpoint | fair |
| 2. Confidence Premium (valuation - fundamentals percentile) | +29.3 | overvalued |
| 3. Multiples vs own 2-year history (median rank, 0-100) | 79 | overvalued |

Price $3.45; price implied by fair value midpoint $1.85. Verdict = majority of the three checks (Mixed if no two agree).

| Multiple | Today | 2-year median | Rank (0-100) | Fair value at median |
|---|---:|---:|---:|---:|
| Market cap / revenue (fees burned, annualised) | 4,902.6x | 1,531.2x | 79 | $1.41B |
| Market cap / DEX volume (annualised) | 0.09x | 0.10x | 48 | $4.59B |
| Market cap / TVL | 22.7x | 20.4x | 71 | $4.07B |
| Market cap / stablecoin supply | 34.9x | 15.1x | 92 | $1.95B |
| Market cap per returning account | $80.59K | $28.99K | 83 | $1.63B |

90-day forward price change by fair-value position (descriptive, overlapping windows):

| After | Days | Median | Mean | Share positive |
|---|---:|---:|---:|---:|
| market cap below band | 62 | -0.5% | +17.8% | 48.4% |
| market cap inside band | 556 | -10.4% | +7.6% | 39.9% |
| market cap above band | 19 | -56.0% | -53.3% | 0.0% |

## Indices (0-100, percentile vs the chain's own trailing 365 days)

| | NEAR | AVAX |
|---|---:|---:|
| Network pillar | 51.9 | 27.4 |
| DeFi pillar | 81.7 | 24.3 |
| Tokenomics pillar | 35.9 | 11.5 |
| **Fundamentals Index** | 56.5 | 21.0 |
| **Valuation Index** | 85.7 | 30.2 |
| **Confidence Premium** (Valuation - Fundamentals) | 29.3 | 9.2 |

- NEAR: valuation runs ahead of fundamentals (confidence premium).
- AVAX: valuation roughly in line with fundamentals.

### Robustness (2000 random weightings of pillars and metrics)

| | median | 5th pct | 95th pct | share of draws < 0 |
|---|---:|---:|---:|---:|
| NEAR premium | 30.1 | 11.1 | 43.8 | 0% |
| AVAX premium | 9.7 | -0.4 | 16.5 | 5% |
| NEAR minus AVAX | 21.2 | 3.2 | 32.8 | 3% |

### Does the premium predict returns? (90-day forward price change, descriptive)

| Chain | Bucket | Days | Median | Mean | Share positive |
|---|---|---:|---:|---:|---:|
| NEAR | premium <= -15 | 255 | -6.6% | +8.9% | 44.3% |
| NEAR | -15 < premium < +15 | 362 | -9.8% | -2.6% | 36.7% |
| NEAR | premium >= +15 | 221 | -19.0% | +13.1% | 44.8% |
| AVAX | premium <= -15 | 581 | -4.1% | +1.7% | 44.4% |
| AVAX | -15 < premium < +15 | 158 | -36.1% | -29.1% | 15.8% |
| AVAX | premium >= +15 | 36 | -43.0% | -47.2% | 0.0% |

Overlapping windows over a single two-year regime: read this as a description, not a trading signal.

## Appendix: NEAR vs AVAX snapshot (trailing 30 days)

| Metric | NEAR | AVAX | NEAR / AVAX |
|---|---:|---:|---:|
| Price | $3.45 | $8.17 | 0.42 |
| Market cap | $4.52B | $3.65B | 1.24 |
| Fully diluted value | $4.52B | $3.85B | 1.17 |
| Fees, annualised (30d) | $1.30M | $4.32M | 0.30 |
| Revenue = fees burned, annualised (30d) | $921.99K | $4.32M | 0.21 |
| DeFi TVL | $160.86M | $589.60M | 0.27 |
| DEX volume, annualised (30d) | $48.14B | $30.09B | 1.60 |
| Stablecoin supply | $133.39M | $815.61M | 0.16 |
| Active accounts / day (30d avg) | 65,578 | 64,842 | 1.01 |
| Returning share of active (30d) | 83.8% | 66.1% | 1.27 |
| Transactions / day (30d avg) | 677,546 | 306,355 | 2.21 |
| Staked share of circulating | 47.2% | 45.5% | 1.04 |
| Net supply growth, last 365d | +2.5% | n/a |  |
| Net supply growth, annualised (last 30d) | +2.5% | +8.6% |  |
| Gross issuance offset by burn (30d) | 0.7% | 1.4% | 0.49 |
| **Market cap / revenue** | 4,902.6x | 843.3x | 5.81 |
| Market cap / fees | 3,477.1x | 843.3x | 4.12 |
| Market cap / TVL | 28.1x | 6.19x | 4.54 |
| FDV / TVL | 28.1x | 6.53x | 4.30 |
| Market cap / DEX volume | 0.09x | 0.12x | 0.77 |
| Market cap / stablecoins | 33.9x | 4.47x | 7.58 |
| Market cap per active account | $68.93K | $56.25K | 1.23 |
| Revenue per active account (annual) | $14.06 | $66.70 | 0.21 |
| YoY active accounts | -74.8% | -70.4% |  |
| YoY transactions | -84.5% | -85.9% |  |
| YoY fees | -52.8% | -50.8% |  |
| YoY TVL | +34.7% | -66.4% |  |
| YoY DEX volume | +5.2% | -70.8% |  |
| YoY stablecoins | -38.4% | -50.4% |  |
| YoY market cap | +92.4% | -50.9% |  |

Notes: AVAX figures are the C-chain (Avalanche L1s excluded). Active accounts = daily distinct signers (NEAR: NearBlocks; AVAX: `activeSenders`). Revenue = fees burned: 70% of NEAR fees (30% go to contract developers), 100% of AVAX C-chain fees. AVAX FDV uses today's total supply. NEAR staking history is collected one snapshot per run (3 so far), so NEAR's staking score starts once enough snapshots accrue.
