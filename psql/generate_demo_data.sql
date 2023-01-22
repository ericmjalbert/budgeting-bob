-- This changes all the transaction data to be random and a bit anonlymized. 
CREATE TABLE IF NOT EXISTS demo_data AS 
WITH account_number_mapper AS (
    SELECT
        number,
        CASE rank() over (order by number) % 4
            WHEN 0 THEN '1111'
            WHEN 1 THEN '2222'
            WHEN 2 THEN '3333'
            WHEN 3 THEN '4444'
            END AS demo_number 
    FROM accounts
)

SELECT
    id,
    CASE demo_number 
        WHEN '1111' THEN 'Savings'
        WHEN '2222' THEN 'Visa'
        WHEN '3333' THEN 'Savings'
        WHEN '4444' THEN 'Visa'
        END AS account_type,
    anm.demo_number AS account_number,
    '2020-01-01'::TIMESTAMP + interval '1 day' * DATE_PART('day', transaction_date - '2019-11-01') / 1.7 AS transaction_date,
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


-- The anonlymized demo transactions are copied.
-- In Fly.io this is sent to the `/` folder of the running VM. We can get this 
-- with `flyctl ssh sftp shell` to bring it to local machine.
\copy public.demo_data TO 'demo_data.csv' csv header;


-- clean up prod DB
DROP TABLE public.demo_data;
