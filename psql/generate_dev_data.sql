-- This changes all the transaction data to be random and a bit anonlymized. 
CREATE TABLE IF NOT EXISTS dev_data AS 
WITH account_number_mapper AS (
    SELECT
        number,
        CASE rank() over (order by number) % 4
            WHEN 0 THEN '1111'
            WHEN 1 THEN '2222'
            WHEN 2 THEN '3333'
            WHEN 3 THEN '4444'
            END AS dev_number 
    FROM accounts
)

SELECT
    id,
    CASE dev_number 
        WHEN '1111' THEN 'Savings'
        WHEN '2222' THEN 'Visa'
        WHEN '3333' THEN 'Savings'
        WHEN '4444' THEN 'Visa'
        END AS account_type,
    anm.dev_number AS account_number,
    '2020-01-01'::TIMESTAMP + interval '1 day' * (random() * DATE_PART('day', current_date - '2020-01-01'::TIMESTAMP)) as transaction_date,
    CASE 
        WHEN value > 0 and category NOT IN ('salary', 'transfer_between_accounts') THEN 'other_earnings' 
        ELSE category
        END AS category,
    ROUND((value * (RANDOM()+1) * 3)::numeric, 2) AS value,
    'just ' || category || ' stuff' AS description_1,
    NULL AS description_2,
    transaction_date AS created,
    transaction_date AS updated
FROM transactions AS t
INNER JOIN account_number_mapper AS anm
    ON account_number = anm.number
WHERE transaction_date > '2019-11-01'
    AND category != 'transfer_between_accounts'
;

-- TODO add a bit here to also copy the split_transactions rows
CREATE TABLE IF NOT EXISTS dev_data_split_transactions AS 
WITH account_number_mapper AS (
    SELECT
        number,
        CASE rank() over (order by number) % 4
            WHEN 0 THEN '1111'
            WHEN 1 THEN '2222'
            WHEN 2 THEN '3333'
            WHEN 3 THEN '4444'
            END AS dev_number 
    FROM accounts
)

SELECT
    id,
    CASE dev_number 
        WHEN '1111' THEN 'Savings'
        WHEN '2222' THEN 'Visa'
        WHEN '3333' THEN 'Savings'
        WHEN '4444' THEN 'Visa'
        END AS account_type,
    anm.dev_number AS account_number,
    '2020-01-01'::TIMESTAMP + interval '1 day' * (random() * DATE_PART('day', current_date - '2020-01-01'::TIMESTAMP)) as transaction_date,
    CASE 
        WHEN value > 0 and category NOT IN ('salary', 'transfer_between_accounts') THEN 'other_earnings' 
        ELSE category
        END AS category,
    ROUND((value * (RANDOM()+1) * 3)::numeric, 2) AS value,
    'just ' || category || ' stuff' AS description_1,
    NULL AS description_2,
    transaction_date AS created,
    transaction_date AS updated
FROM transactions AS t
INNER JOIN account_number_mapper AS anm
    ON account_number = anm.number
WHERE transaction_date > '2019-11-01'
    AND category != 'transfer_between_accounts'
;


-- The anonlymized dev transactions are copied.
-- In Fly.io this is sent to the `/` folder of the running VM. We can get this 
-- with `flyctl ssh sftp shell` to bring it to local machine and then used to 
-- initialize the local dev docker psql.
\copy public.dev_data TO 'dev_data.csv' csv header;
\copy public.dev_data_split_transactions TO 'dev_data_split_transactions.csv' csv header;


-- clean up prod DB
DROP TABLE public.dev_data;
DROP TABLE public.dev_data_split_transactions;
