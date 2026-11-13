-- Daily active accounts (distinct transaction signers) and transaction count.
-- Partition filter on block_date keeps the scan to the requested days only.
SELECT
  block_date,
  COUNT(DISTINCT signer_account_id) AS active_accounts,
  COUNT(*)                          AS transactions
FROM `bigquery-public-data.crypto_near_mainnet_us.transactions`
WHERE block_date BETWEEN @start_date AND @end_date
GROUP BY block_date
ORDER BY block_date;
