# X thread: NEAR HACKATHON demo post

Post these in order as one thread. Attach the listed images to each post (X allows up to 4 images per post, or one
video). The images come from the live dashboard and are in this folder.

Before posting, check the numbers against https://almondxxx.github.io/nearthesis/ on the day you post. The dashboard
refreshes daily, so figures can shift slightly.

---

## Post 1
**Attach:** the demo video (60–90 s). If you don't have one yet, use `5-answers.png`.

```
Everyone says NEAR Intents volume is the leading signal for NEAR adoption. I tested it on 100 weeks of on-chain data.

Result: Intents moves WITH usage, not ahead of it. Price leads it just as often.

Built at #NEARHackathon @NEARProtocol 🧵
```

## Post 2
**Attach:** `2-real-usage-index.png`

```
How I tested it:
• Intents volume (DefiLlama) + 1,362 sampled hours of swaps (Intents Explorer API)
• vs NEAR price, with BTC as a market control
• Target: returning signers + fees burned (BigQuery). Hard to fake with bots
• Weekly changes, out-of-sample tests
```

## Post 3
**Attach:** `3a-head-to-head.png`, `3c-lead-lag.png`, `3b-same-week-scatter.png`

```
What I found:
• Same week, Intents tracks NEAR transactions (r=+0.40) and fees (+0.38) better than price does
• But it doesn't lead real usage
• ~88K tx/day hit intents.near from ~166 signers. Volume runs through solvers, not new users
```

## Post 4
**Attach:** `4-fees-per-1m.png`

```
Value capture: NEAR fees per $1M of Intents volume fell from $807 (Q3 '25) to $19 (Q3 '26).

Volume is booming. NEAR's cut of it isn't.
```

## Post 5
**Attach:** `5-answers.png`

```
Live dashboard, every chart shows the query behind it: https://almondxxx.github.io/nearthesis/
Repo (one command rebuilds everything): https://github.com/almondxxx/nearthesis

What would you use as "real usage" on NEAR? @NearBuilders @NearLegion
```

---

## Image key
| File | What it shows |
|---|---|
| `2-real-usage-index.png` | The target: returning signers and fees burned, indexed to 100 |
| `3a-head-to-head.png` | Intents vs price on 6 adoption metrics: same-week links, leads, which leads better |
| `3c-lead-lag.png` | Correlation with real usage 0–8 weeks ahead: Intents has 0 significant leads, price has 2 |
| `3b-same-week-scatter.png` | Weekly Intents growth vs transaction growth, r = +0.40 |
| `4-fees-per-1m.png` | NEAR fees per $1M of Intents volume over time |
| `5-answers.png` | The three answers: Q1 PARTLY, Q2 MIXED, Q3 PARTLY |

## Demo video shot list (60–90 s)
1. Main page: the three answer cards (10 s)
2. The Q1/Q2 lead-lag chart: Intents has no significant point after week 0 (20 s)
3. Correlation page: the head-to-head table, then select Transactions to show the same-week scatter (20 s)
4. The fees per $1M chart (15 s)
5. Expand "Query behind this chart" to show the SQL (10 s)
