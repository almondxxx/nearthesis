# NEAR investment thesis: flow without capture

Figures are as of **2026-11-12**, the snapshot committed with this file. The live numbers are in
[`reports/latest.md`](reports/latest.md) and on the dashboard; both regenerate on every pipeline run.
Each figure below comes from `data/processed/*.csv`, so you can check it by running `python run.py --offline`.

## The question

How much confidence are investors placing in NEAR, and is it earned? The **Confidence Premium** measures this.
It is NEAR's Valuation Index minus its Fundamentals Index, both scored against NEAR's own previous 365 days.
The same measure is applied to Avalanche (C-chain) as a peer.

## The answer in one line

**Investors are paying ahead of NEAR's fundamentals (premium +28.6), and the cause is DeFi order flow, mostly
NEAR Intents, not L1 usage or fee revenue. The long-term case depends on that flow turning into value
for the token. The data doesn't show that happening yet.**

## Evidence

### 1. Confidence is high, and the reading holds under different weights
| | NEAR | AVAX |
|---|---:|---:|
| Fundamentals Index | 57.7 | 20.0 |
| Valuation Index | 86.3 | 29.9 |
| Confidence Premium | **+28.6** | +9.9 |
| Premium under 2,000 random weightings (5th to 95th percentile) | +7.3 to +44.3 | +1.7 to +15.9 |
| Share of weightings where the premium is negative | 0% | 3% |

Over the two-year window, NEAR's premium ranged from **-48.9** (15 Feb 2026, near the price bottom)
to **+53.9** (21 Sep 2026). The premium has moved with price swings while fundamentals moved slowly.

**The premium is a confidence gauge, not a timing tool.** Over the 90 days after a reading of -15 or lower,
NEAR's median price change was -6.6%. After a reading of +15 or higher it was -19.0%. But the *mean* was higher after
high readings (+13.1% vs +8.9%), and the share of positive outcomes was the same (about 44%). On this sample the
premium doesn't predict returns reliably. It describes the price relative to fundamentals, nothing more. The full
backtest table is in `reports/latest.md`.

### 2. The growth is DeFi flow, and almost all of it is NEAR Intents
- DEX volume on NEAR went from about **$8M/day (Q4 2024) to $141M/day (Q4 2026)**, about 17x.
  Annualised, it is **$49B, 1.6x AVAX's $30.5B**, while AVAX DEX volume fell 72% year on year.
- Over the last 30 days **NEAR Intents is 93% of NEAR DEX volume** on DefiLlama. Rhea is about 7%.
- TVL is up 39% year on year, to $168M. AVAX TVL is down 67%, to $609M.
- NEAR's DeFi pillar is at **88**, the highest of the three pillars on either chain.

### 3. The flow doesn't reach L1 revenue
- NEAR fees **fell** from about $23K/day (Q4 2024) to about $5.5K/day while DEX volume grew 17x.
  Intents settlement costs very little gas, so cross-chain volume brings in almost no L1 fees.
- Market cap / revenue (fees burned, annualised) is **4,202x for NEAR and 910x for AVAX**.
  NEAR's multiple divided by AVAX's rose from about **0.6 (Q1 2025) to 4.5 (Q4 2026)**.
- Revenue per active account is **$17.5 a year on NEAR and $63.8 on AVAX**.
- Market cap / stablecoin supply is **36x for NEAR and 4.2x for AVAX**. NEAR's stablecoin base ($131M) is down 41% year on year.

### 4. Tokenomics: the inflation cut is real, and burn hardly matters
- Net supply growth fell from **5.0% a year (2024 to Sep 2025) to 2.5% a year (Nov 2025 onward)**. The
  supply data shows the step clearly, and it is the largest tokenomics improvement either chain made in the window.
- Fee burn offsets only **0.8%** of NEAR's gross issuance. AVAX burn offsets 1.5%. Neither chain
  has a protocol-level buyback, so net supply on both chains depends almost entirely on issuance policy.
- Staked share: **NEAR 44.3%, AVAX 45.6%** (latest snapshots). The two are close.

### 5. User numbers: raw activity is bot-driven, the returning base is stable
- NEAR daily signers fell from 1.2M to 1.9M a day (quarterly averages in 2024) to about 64K. Almost all of the drop is *new* accounts
  (about 400K/day at the peak of airdrop farming, about 9.5K/day now). AVAX shows the same pattern the other way
  round: senders jumped to about 1.4M/day from Jan to Jul 2026, then fell to about 65K.
- Returning accounts (active minus new) bottomed at about **45K/day in Q4 2025 and recovered to about 65K/day**.
  83% of NEAR's current signers are returning users, against 68% on AVAX. NEAR's user base is smaller
  but stickier than the raw counts suggest.

## Thesis

1. **Bull case:** NEAR has become a cross-chain trading venue: Intents processes more DEX volume than the AVAX
   C-chain. The inflation cut halved dilution, and the remaining users are real, returning users. If this flow is
   priced as "chain abstraction infrastructure" rather than as L1 gas demand, the current multiples
   aren't comparable to an L1's.
2. **What the data doesn't support yet:** value capture. NEAR is more expensive than AVAX on revenue (4.6x), fees (3.2x),
   TVL (4.5x) and stablecoins (8.6x), and cheaper only per dollar of DEX volume (0.77x). Burn is negligible, and fees
   are falling while volume grows. The +28.6 premium means the market already expects capture that hasn't happened.
3. **Position:** a long-term holding is justified by the flow and the lower dilution, but not at a high premium.
   I tested a simple entry rule, **Confidence Premium ≤ -15 while the DeFi pillar is ≥ 50**, and it
   did **not** work. It held on only 14 days (last on 2025-11-22), and the median 90-day price change after them was -21%.
   So the case rests on the value-capture checks below, not on timing the premium.

## What would change my mind (falsifiers, all tracked on the dashboard)
- **NEAR DEX volume turns negative year on year** for a full quarter: the main driver of the thesis has failed.
- **Revenue per active account starts rising** with no premium increase: that is evidence of value capture,
  and an argument for holding a larger position.
- **Net supply growth rises back above 2.5%**, or the staked share falls below 40%: the tokenomics have gotten worse.
- **The NEAR ÷ AVAX market cap / revenue ratio falls back toward 1** without the price falling:
  revenue is catching up with valuation.

## Caveats
- Activity counts on both chains are distorted by bots and campaigns, which is why the index scores each chain
  against its own history and gives returning accounts the same weight as raw activity.
- AVAX is the C-chain only. Avalanche L1 activity isn't counted.
- NEAR stake history isn't available without an API key. The pipeline saves one stake snapshot per run, so
  NEAR's staking score will join the index on its own once 180 snapshots exist.
- AVAX circulating supply before CoinGecko's 365-day public window is extrapolated, and used only for market cap.
- This is research, not investment advice.
