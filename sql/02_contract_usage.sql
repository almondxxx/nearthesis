-- Daily contract usage from the transactions table (cheap: ~3 narrow columns).
-- distinct_receivers: accounts/contracts that received at least one transaction
-- intents_direct_txs / _signers: transactions sent straight to intents.near
-- (Receipt-level function calls are in sql/optional/02b_contract_usage_receipts.sql;
--  that version scans ~318 GB per 6 months, so it is not run by default.)
SELECT
  block_date,
  COUNT(DISTINCT receiver_account_id)                                   AS distinct_receivers,
  COUNTIF(receiver_account_id = 'intents.near')                         AS intents_direct_txs,
  COUNT(DISTINCT IF(receiver_account_id = 'intents.near', signer_account_id, NULL)) AS intents_direct_signers
FROM `bigquery-public-data.crypto_near_mainnet_us.transactions`
WHERE block_date BETWEEN @start_date AND @end_date
GROUP BY block_date
ORDER BY block_date;
