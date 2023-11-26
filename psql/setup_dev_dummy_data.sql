\copy public.transactions FROM '/opt/dev_data_transactions.csv' WITH (FORMAT csv, HEADER);
\copy public.split_transactions FROM '/opt/dev_data_split_transactions.csv' WITH (FORMAT csv, HEADER);


-- Fill the accounts and budget with fake data
INSERT INTO public.accounts VALUES
(1111, 'Savings', 'Bill', 'Savings', 100, TRUE, 'RBC'),
(2222, 'Visa', 'Bill', 'Visa', 200, TRUE, 'RBC'),
(3333, 'Savings', 'Billette', 'Savings', 300, TRUE, 'RBC'),
(4444, 'Visa', 'Billette', 'Visa', 400, TRUE, 'RBC')
;

INSERT INTO public.budgets (category_id, budget, updated_month) VALUES
(1, 1000, '2020-01-01'),
(2, 1000, '2020-01-01'),
(3, 1000, '2020-01-01'),
(4, 1000, '2020-01-01'),
(5, 1000, '2020-01-01'),
(6, 1000, '2020-01-01'),
(7, 1000, '2020-01-01'),
(8, 1000, '2020-01-01'),
(9, 1000, '2020-01-01'),
(10, 1000, '2020-01-01'),
(11, 1000, '2020-01-01'),
(12, 1000, '2020-01-01'),
(13, 1000, '2020-01-01'),
(14, 1000, '2020-01-01'),
(15, 1000, '2020-01-01'),
(16, 10000, '2020-01-01'),
(17, 100800, '2020-01-01'),
(18, 10000, '2020-01-01'),
(19, 1000, '2020-01-01'),
(20, -9000, '2020-01-01'),
(21, 0, '2020-01-01'),
(22, 0, '2020-01-01'),
(23, -700, '2020-01-01'),
(24, -80000, '2020-01-01'),
(25, 0, '2020-01-01'),
(26, 0, '2020-01-01'),
(2, 20000, '2021-01-01'),
(27, 550, '2022-04-01'),
(28, 9400, '2022-07-01'),
(29, 800, '2022-05-01'),
(30, 800, '2022-05-01'),
(31, 800, '2022-05-01'),
(32, 800, '2022-05-01'),
(33, 800, '2023-01-01')
ON CONFLICT DO NOTHING
;

