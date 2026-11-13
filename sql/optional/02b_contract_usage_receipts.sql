-- OPTIONAL, NOT RUN BY DEFAULT: scans ~318 GB per 6 months of data (BigQuery free tier is 1 TB/month).
-- Daily contract usage: function-call receipts, distinct contracts called,
-- and on-chain activity of the NEAR Intents contract (intents.near).
-- Partition filter on block_date keeps the scan to the requested days only.
SELECT
  block_date,
  COUNT(*)                                     AS function_calls,
  COUNT(DISTINCT receipt_receiver_account_id)  AS contracts_called,
  COUNTIF(receipt_receiver_account_id = 'intents.near') AS intents_contract_calls,
  COUNT(DISTINCT IF(receipt_receiver_account_id = 'intents.near',
                    receipt_predecessor_account_id, NULL)) AS intents_contract_callers
FROM `bigquery-public-data.crypto_near_mainnet_us.receipt_actions`
WHERE block_date BETWEEN @start_date AND @end_date
  AND action_kind = 'FUNCTION_CALL'
GROUP BY block_date
ORDER BY block_date;
