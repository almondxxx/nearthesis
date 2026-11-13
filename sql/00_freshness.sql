-- Is the NEAR BigQuery dataset still updating?
-- NEAR Lake (its source) was deprecated on 2026-03-24, so check before trusting recent dates.
-- Reads partition metadata only (no table scan, no query cost).
SELECT
  table_name,
  MAX(partition_id) AS latest_partition,   -- YYYYMMDD of the newest block_date
  SUM(total_rows)   AS total_rows
FROM `bigquery-public-data.crypto_near_mainnet_us.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name IN ('transactions', 'receipt_actions')
  AND partition_id NOT IN ('__NULL__', '__UNPARTITIONED__')
GROUP BY table_name;
