-- This needs to be run on the postgres database after it has been initialized with the tables

---------
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
;



---------
CREATE OR REPLACE VIEW public.monthly_spend
AS

SELECT
    mb.category,
    mb.month,
    COALESCE(SUM(-1 * transactions.value), 0) AS spend
FROM public.monthly_budget AS mb
LEFT JOIN public.transactions
    ON transactions.category = mb.category
    AND DATE_TRUNC('month', transactions.transaction_date) = mb.month
GROUP BY 1, 2
;


---------
CREATE OR REPLACE VIEW public.cumulative_budget
AS

SELECT
    category,
    month,
    SUM(budget) OVER (PARTITION BY category ORDER BY month) AS budget,
    SUM(budget) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS budget_6m,
    SUM(budget) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 12 PRECEDING AND CURRENT ROW) AS budget_12m,
    SUM(budget) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 24 PRECEDING AND CURRENT ROW) AS budget_24m
FROM public.monthly_budget
;


---------
CREATE OR REPLACE VIEW public.cumulative_spend
AS

SELECT
    category,
    month,
    SUM(spend) OVER (PARTITION BY category ORDER BY month) AS spend,
    SUM(spend) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS spend_6m,
    SUM(spend) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 12 PRECEDING AND CURRENT ROW) AS spend_12m,
    SUM(spend) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 24 PRECEDING AND CURRENT ROW) AS spend_24m
FROM public.monthly_spend
;


---------
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
