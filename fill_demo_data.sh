#!/bin/bash

PSQL="heroku pg:psql --app budgeting-bob"
PSQL_DEMO="heroku pg:psql --app budgeting-bob-demo"

$PSQL -c "
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
    NULL AS description_1,
    NULL AS description_2,
    NULL AS created,
    NULL AS updated
FROM transactions AS t
INNER JOIN account_number_mapper AS anm
    ON account_number = anm.number
WHERE transaction_date > '2019-11-01'
    AND category != 'transfer_between_accounts'
"

$PSQL -c '\copy public.demo_data TO 'demo_data.csv' csv header'

$PSQL -c "
DROP TABLE public.demo_data;
"

$PSQL_DEMO -c "
DROP TABLE public.transactions;
"

$PSQL_DEMO -c "
CREATE TABLE IF NOT EXISTS public.transactions (
    id TEXT,
    account_type TEXT,
    account_number TEXT,
    transaction_date TIMESTAMP WITHOUT TIME ZONE,
    category TEXT,
    value FLOAT,
    description_1 TEXT,
    description_2 TEXT,
    created TIMESTAMP WITHOUT TIME ZONE,
    updated TIMESTAMP WITHOUT TIME ZONE
)
"

$PSQL_DEMO -c '\copy public.transactions FROM 'demo_data.csv' WITH (FORMAT csv, HEADER);'

$PSQL_DEMO -c "
UPDATE public.transactions
SET created = transaction_date,
    updated = transaction_date,
    description_1 = 'Just ' || category || ' stuff'
"

rm demo_data.csv
