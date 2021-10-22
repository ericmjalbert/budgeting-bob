#!/bin/bash

## This needs to be run on the postgres database after it has been initialized

PSQL="heroku pg:psql --app budgeting-bob"

##### Budget VIEWS
$PSQL -c "
CREATE VIEW public.monthly_budget
AS

WITH monthly_budget AS (
    SELECT
        ca.category,
        month::DATE,
        bu.budget,
        SUM(CASE WHEN bu.budget IS NULL THEN 0 ELSE 1 END) OVER (PARTITION BY category ORDER BY month) as value_partition
    FROM public.categories_new AS ca
    CROSS JOIN GENERATE_SERIES('2020-01-01', CURRENT_DATE, '1 month') AS month
    LEFT JOIN public.budgets AS bu
        ON bu.category_id = ca.id
        AND bu.updated_month = month::DATE
)

SELECT
    category,
    month,
    FIRST_VALUE(budget) OVER (PARTITION BY category, value_partition ORDER BY month) AS budget
FROM monthly_budget
"


$PSQL -c "
CREATE VIEW public.monthly_spend
AS

WITH all_spends AS (
    SELECT
        category,
        DATE_TRUNC('month', transaction_date) AS spend_month,
        -1 * value as value
    FROM public.transactions
    UNION ALL SELECT
        category,
        DATE_TRUNC('month', shipped_date::timestamp) AS spend_month,
        quantity * price AS value
    FROM public.amazon_items
    WHERE shipped_date NOT LIKE 'Not delivered %'
)

SELECT
    mb.category,
    mb.month,
    COALESCE(SUM(all_spends.value), 0) AS spend
FROM public.monthly_budget AS mb
LEFT JOIN all_spends
    ON all_spends.category = mb.category
    AND all_spends.spend_month = mb.month
GROUP BY 1, 2
"


$PSQL -c "
CREATE VIEW public.cumulative_budget
AS

SELECT
    category,
    month,
    SUM(budget) OVER (PARTITION BY category ORDER BY month) AS budget
FROM public.monthly_budget
"


$PSQL -c "
CREATE VIEW public.cumulative_spend
AS

SELECT
    category,
    month,
    SUM(spend) OVER (PARTITION BY category ORDER BY month) AS spend
FROM public.monthly_spend
"



$PSQL -c "
CREATE VIEW public.monthly_remaining
AS

SELECT
    mb.category,
    mb.month,
    mb.budget,
    mb.budget - COALESCE(ms.spend, 0) AS remaining,
    case
        when mb.budget - COALESCE(ms.spend, 0) < -1 * mb.budget / 2 then 'very over budget'
        when mb.budget - COALESCE(ms.spend, 0) < 0 then 'over budget'
        when mb.budget - COALESCE(ms.spend, 0) >= 0 then 'under budget'
        end as status,
    -- need this column for bootstrap coloring
    case
        when mb.budget - COALESCE(ms.spend, 0) < -1 * mb.budget / 2 then 'table-danger'
        when mb.budget - COALESCE(ms.spend, 0) < 0 then 'table-warning'
        when mb.budget - COALESCE(ms.spend, 0) >= 0 then 'table-success'
        end as status_class
FROM public.monthly_budget AS mb
LEFT JOIN public.monthly_spend AS ms
    USING (category, month)
WHERE mb.category != 'transfer_between_accounts'
    AND mb.budget > 0
"
