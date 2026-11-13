-- Weekly returning signers: accounts that signed a transaction in a week AND in
-- any of the 4 previous weeks. A repeat user is much harder to fake than a new
-- account. Weeks run Monday-Sunday; block_date = the week's Sunday.
-- Partition filter on block_date (plus a 28-day look-back) keeps the scan bounded.
WITH weekly AS (
  SELECT DISTINCT
    DATE_TRUNC(block_date, WEEK(MONDAY)) AS week,
    signer_account_id
  FROM `bigquery-public-data.crypto_near_mainnet_us.transactions`
  WHERE block_date BETWEEN DATE_SUB(@start_date, INTERVAL 28 DAY) AND @end_date
)
SELECT
  DATE_ADD(w.week, INTERVAL 6 DAY)            AS block_date,
  COUNT(DISTINCT w.signer_account_id)         AS weekly_signers,
  COUNT(DISTINCT IF(p.signer_account_id IS NOT NULL, w.signer_account_id, NULL)) AS returning_signers
FROM weekly w
LEFT JOIN weekly p
  ON p.signer_account_id = w.signer_account_id
 AND p.week BETWEEN DATE_SUB(w.week, INTERVAL 4 WEEK) AND DATE_SUB(w.week, INTERVAL 1 WEEK)
WHERE w.week >= DATE_TRUNC(@start_date, WEEK(MONDAY))
  AND DATE_ADD(w.week, INTERVAL 6 DAY) <= @end_date          -- complete weeks only
GROUP BY w.week
ORDER BY w.week;
