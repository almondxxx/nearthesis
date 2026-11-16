# NEAR valuation check - latest numbers

_Generated automatically by `python run.py`. Data as of **2026-11-15** (fetched 2026-11-16T03:16:34Z). Do not edit by hand: the next pipeline run overwrites this file._

## Verdict: **Overvalued**

| Check | Reading | Signal |
|---|---:|---|
| 1. Fair value (NEAR's median multiples over 2 years) | market cap $3.97B vs fair value $2.43B (band $1.83B - $5.17B), +63.6% vs midpoint | fair |
| 2. Confidence Premium (valuation - fundamentals percentile) | +29.6 | overvalued |
| 3. Multiples vs own 2-year history (median rank, 0-100) | 76 | overvalued |

Price $3.03; price implied by fair value midpoint $1.85. Verdict = majority of the three checks (Mixed if no two agree).

| Multiple | Today | 2-year median | Rank (0-100) | Fair value at median |
|---|---:|---:|---:|---:|
| Market cap / revenue (fees burned, annualised) | 4,342.7x | 1,532.5x | 76 | $1.40B |
| Market cap / DEX volume (annualised) | 0.08x | 0.10x | 39 | $4.66B |
| Market cap / TVL | 20.3x | 20.4x | 48 | $4.00B |
| Market cap / stablecoin supply | 30.6x | 15.1x | 92 | $1.95B |
| Market cap per returning account | $69.79K | $29.02K | 79 | $1.65B |

90-day forward price change by fair-value position (descriptive, overlapping windows):

| After | Days | Median | Mean | Share positive |
|---|---:|---:|---:|---:|
| market cap below band | 62 | -0.5% | +17.8% | 48.4% |
| market cap inside band | 557 | -10.4% | +7.7% | 40.0% |
| market cap above band | 19 | -56.0% | -53.3% | 0.0% |

## Indices (0-100, percentile vs the chain's own trailing 365 days)

| | NEAR | AVAX |
|---|---:|---:|
| Network pillar | 53.0 | 27.4 |
| DeFi pillar | 81.6 | 24.5 |
| Tokenomics pillar | 33.0 | 10.5 |
| **Fundamentals Index** | 55.8 | 20.8 |
| **Valuation Index** | 85.4 | 29.4 |
| **Confidence Premium** (Valuation - Fundamentals) | 29.6 | 8.6 |

- NEAR: valuation runs ahead of fundamentals (confidence premium).
- AVAX: valuation roughly in line with fundamentals.

### Robustness (2000 random weightings of pillars and metrics)

| | median | 5th pct | 95th pct | share of draws < 0 |
|---|---:|---:|---:|---:|
| NEAR premium | 30.2 | 11.3 | 45.4 | 0% |
| AVAX premium | 9.1 | -1.3 | 16.3 | 7% |
| NEAR minus AVAX | 22.4 | 4.3 | 33.6 | 2% |

### Does the premium predict returns? (90-day forward price change, descriptive)

| Chain | Bucket | Days | Median | Mean | Share positive |
|---|---|---:|---:|---:|---:|
| NEAR | premium <= -15 | 255 | -6.6% | +8.9% | 44.3% |
| NEAR | -15 < premium < +15 | 363 | -9.8% | -2.3% | 36.9% |
| NEAR | premium >= +15 | 221 | -19.0% | +13.1% | 44.8% |
| AVAX | premium <= -15 | 582 | -4.0% | +1.7% | 44.5% |
| AVAX | -15 < premium < +15 | 158 | -36.1% | -29.1% | 15.8% |
| AVAX | premium >= +15 | 36 | -43.0% | -47.2% | 0.0% |

Overlapping windows over a single two-year regime: read this as a description, not a trading signal.

## Appendix: NEAR vs AVAX snapshot (trailing 30 days)

| Metric | NEAR | AVAX | NEAR / AVAX |
|---|---:|---:|---:|
| Price | $3.03 | $6.83 | 0.44 |
| Market cap | $3.97B | $3.05B | 1.30 |
| Fully diluted value | $3.97B | $3.22B | 1.23 |
| Fees, annualised (30d) | $1.28M | $4.32M | 0.30 |
| Revenue = fees burned, annualised (30d) | $914.65K | $4.32M | 0.21 |
| DeFi TVL | $143.56M | $541.42M | 0.27 |
| DEX volume, annualised (30d) | $48.89B | $29.26B | 1.67 |
| Stablecoin supply | $132.28M | $809.47M | 0.16 |
| Active accounts / day (30d avg) | 66,346 | 64,645 | 1.03 |
| Returning share of active (30d) | 84.0% | 66.3% | 1.27 |
| Transactions / day (30d avg) | 678,677 | 308,470 | 2.20 |
| Staked share of circulating | 47.2% | 45.5% | 1.04 |
| Net supply growth, last 365d | +2.5% | n/a |  |
| Net supply growth, annualised (last 30d) | +2.5% | +8.2% |  |
| Gross issuance offset by burn (30d) | 0.7% | 1.4% | 0.48 |
| **Market cap / revenue** | 4,342.7x | 705.6x | 6.15 |
| Market cap / fees | 3,114.5x | 705.6x | 4.41 |
| Market cap / TVL | 27.7x | 5.63x | 4.92 |
| FDV / TVL | 27.7x | 5.94x | 4.66 |
| Market cap / DEX volume | 0.08x | 0.10x | 0.78 |
| Market cap / stablecoins | 30.0x | 3.76x | 7.98 |
| Market cap per active account | $59.87K | $47.14K | 1.27 |
| Revenue per active account (annual) | $13.79 | $66.80 | 0.21 |
| YoY active accounts | -74.4% | -71.5% |  |
| YoY transactions | -84.4% | -85.9% |  |
| YoY fees | -53.7% | -48.0% |  |
| YoY TVL | +31.9% | -66.2% |  |
| YoY DEX volume | +4.6% | -70.7% |  |
| YoY stablecoins | -37.7% | -50.6% |  |
| YoY market cap | +88.9% | -50.9% |  |

Notes: AVAX figures are the C-chain (Avalanche L1s excluded). Active accounts = daily distinct signers (NEAR: NearBlocks; AVAX: `activeSenders`). Revenue = fees burned: 70% of NEAR fees (30% go to contract developers), 100% of AVAX C-chain fees. AVAX FDV uses today's total supply. NEAR staking history is collected one snapshot per run (4 so far), so NEAR's staking score starts once enough snapshots accrue.
