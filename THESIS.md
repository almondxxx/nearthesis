# Is NEAR undervalued or overvalued?

Figures are as of **2026-11-12**, the snapshot committed with this file. The live numbers are in
[`reports/latest.md`](reports/latest.md) and on the dashboard; both regenerate on every pipeline run.
To check any figure here, run `python run.py --offline`.

## Verdict: **Overvalued**, but within reach of fair value

The verdict uses NEAR's own data only, with no other chain. It runs three independent checks and takes the majority view:

| Check | Reading | Signal |
|---|---|---|
| **1. Fair value**: what NEAR is worth at its own median multiples over the last 2 years | market cap **$4.70B** vs fair value **$2.52B** (band $1.90B–$5.37B) | fair: above the midpoint but inside the band |
| **2. Confidence Premium**: valuation percentile minus fundamentals percentile, 365-day window | **+28.6** | overvalued |
| **3. Multiples vs history**: median rank of today's five multiples in the last 2 years | **76/100** | overvalued |

Two of three checks say overvalued. At the fair-value midpoint NEAR would trade around **$1.92**, against
**$3.59** today. Because the price is still inside the band, the right reading is "priced for growth that
hasn't fully arrived", not "a bubble".

### Why the checks disagree on how far
NEAR is fairly priced on some fundamentals and expensive on others:

| Multiple | Today | 2-year median | Rank | Fair value at median |
|---|---:|---:|---:|---:|
| Market cap / DEX volume | 0.10x | 0.10x | 50 | $4.71B, **in line** |
| Market cap / TVL | 23x | 20x | 73 | $4.17B, slightly rich |
| Market cap / revenue (fees burned) | 4,202x | 1,525x | 76 | $1.71B, **rich** |
| Market cap / stablecoins | 36x | 15x | 93 | $1.95B, **rich** |
| Market cap per returning account | $86.6K | $28.9K | 85 | $1.57B, **rich** |

The market is valuing NEAR on its **DEX flow**, which is mostly NEAR Intents. On that one measure the price is fair.
On every measure of what the chain actually keeps (revenue, the stablecoin base, users), it is expensive.

## Evidence

### 1. The flow is real and growing
- DEX volume on NEAR went from about **$8M/day (Q4 2024) to $141M/day (Q4 2026)**, about 17x. That is **$49B annualised**,
  and up 14.5% year on year.
- Over the last 30 days **NEAR Intents is 93% of NEAR DEX volume** on DefiLlama. Rhea is about 7%.
- TVL is up **39%** year on year, to $168M. The DeFi pillar is at **88/100**, NEAR's strongest.

### 2. The value stays with the flow, not the token
- Fees **fell** from about $23K/day to about $5.5K/day while DEX volume grew 17x. Intents settlement uses almost no gas.
- Fee burn offsets only **0.8%** of gross token issuance. There is no protocol buyback.
- Stablecoin supply is down **41%** year on year, to $131M.

### 3. Tokenomics improved
- Net supply growth fell from **5.0% a year to 2.5% a year** from November 2025. The data shows the inflation cut as a clean step.
- **44.3%** of circulating supply is staked (latest snapshot).

### 4. Users: fewer, but real
- Daily signers fell from 1.2M–1.9M (2024) to about 64K. Almost all of the drop is *new*-account farming disappearing
  (about 400K new accounts a day at the peak, about 9.5K now).
- Returning accounts bottomed at about **45K/day (Q4 2025) and recovered to about 65K/day**. **83%** of today's signers are returning users.

## How reliable is this?
- **Weights:** the Confidence Premium stays positive in **100%** of 2,000 random weightings (5th–95th percentile: +7.3 to +44.3).
- **History:** of the three readings, only "market cap above the fair-value band" has been followed by a clear outcome.
  Market cap was above the band on 55 days. For the 19 that already have 90 days of data after them (late 2024 and
  26 May 2026), the median price change was **-56%**. That is a small sample. The latest episode (18 Sep to 23 Oct 2026,
  36 days) doesn't have 90-day results yet, but market cap has already fallen from about $6.4B back inside the band.
  Readings inside the band (554 days) or below it (62 days) were followed by mixed results.
  The Confidence Premium on its own **does not** predict returns reliably. After a reading of +15 or more, the
  median 90-day change was -19%, but the mean was +13%.
- **What I tested and dropped:** a "premium ≤ -15 and DeFi ≥ 50" entry rule held on only 14 days, and the median 90-day change after them was -21%.

## Thesis
NEAR has become a cross-chain trading venue, its dilution has halved, and its remaining users are real, returning users.
The market already prices that in: NEAR trades at its usual multiple of DEX flow, but at roughly 2–3x its usual
multiple of revenue, stablecoins and users. **For today's price to make sense, Intents flow has to start delivering
value to the NEAR token** through fees, burn or demand for NEAR. Until the data shows that, NEAR is a long-term hold
but expensive at today's price. The model's fair value is $2.52B, about $1.92 a token, with a band of $1.90B–$5.37B.

## What would change the verdict (all tracked on the dashboard)
- **Toward undervalued:** revenue, the stablecoin base or returning accounts grow faster than market cap, pulling those
  multiples back to their medians.
- **Toward overvalued:** market cap breaks above the fair-value band (about $5.4B today). It did so in late 2024
  and from September to October 2026, and both episodes were followed by drawdowns.
- **Thesis broken:** NEAR DEX volume turns negative year on year for a full quarter, or net supply growth rises back above 2.5%.

## Optional context: other chains
The verdict doesn't depend on these. They are on the dashboard as a toggle:
- **L1 basket median** (AVAX, Sui, Aptos, TON, ICP, Cardano). Most L1s shrank over the past year (median DEX volume -74%,
  TVL -71%). NEAR is the only one where TVL and DEX volume both grew. This is the market-wide control.
- **THORChain**, a cross-chain swap venue like NEAR Intents. It also grew its DEX volume (+192%), and its fees grew too
  (+15%), at a market cap / revenue of 869x against NEAR's 4,202x. It shows that a swap venue can earn from its flow.
- **AVAX**: a similar-sized L1, but its trend is opposite to NEAR's, so it's kept for reference only.

### Pump.fun integration (event study)
Pump.fun's app added NEAR tokens on **2026-11-04** and Avalanche tokens right after. Changes in the 8 days since,
each chain against its own previous 14 days:

| | Active accounts | Transactions | Fees | DEX volume |
|---|---:|---:|---:|---:|
| NEAR | +73.7% | +37.3% | -8.2% | +9.8% |
| AVAX (Nov 5, approximate date) | -1.3% | +12.8% | +25.4% | -1.3% |
| L1s Pump.fun didn't add (median) | n/a | n/a | -6.7% | +9.7% |

The same integration brought NEAR far more activity than AVAX, but **NEAR's fees fell while AVAX's rose**, and NEAR's
DEX volume rose no more than the control group's. That is the thesis in miniature: activity arrives, value capture
doesn't. It's 8 days of data and not causal; the dashboard extends the window daily.

## Caveats
- Activity counts are distorted by bots and campaigns, which is why returning accounts are tracked separately.
- NEAR stake history isn't available without an API key. The pipeline saves one stake snapshot per run, so staking joins the index once 180 snapshots exist.
- Peer market caps cover only the last 365 days (CoinGecko's public limit).
- The Pump.fun dates come from secondary reports.
- This is research, not investment advice.
