-- Column names of the tables these queries use (metadata only, no query cost).
SELECT table_name, column_name, data_type
FROM `bigquery-public-data.crypto_near_mainnet_us.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name IN ('transactions', 'receipt_actions')
ORDER BY table_name, ordinal_position;
