CREATE TABLE IF NOT EXISTS public.user (
    id          SERIAL PRIMARY KEY,
    username    TEXT UNIQUE NOT NULL,
    password    TEXT NOT NULL
)
;



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
;



CREATE TABLE IF NOT EXISTS public.categories_new (
    id          SERIAL PRIMARY KEY,
    category    TEXT,
    description TEXT,
    examples    TEXT[]
)
;

INSERT INTO public.categories_new VALUES
(1, 'athletics', 'Things that help us be more althetic', NULL),
(2, 'beauty', 'Things for beauty products or services', NULL),
(3, 'car', 'Money spent on things because we have and use the car', NULL),
(4, 'cats', 'Things for the cats well-being', NULL),
(5, 'clothing', 'Items what we wear for the purpose of fashion or weather', NULL),
(6, 'dates', 'Money spent for date night activities or dinner', NULL),
(7, 'eating', 'Money spent on food for a single person', NULL),
(8, 'entertainment', 'Money spent on games or other entertaining things', NULL),
(9, 'gifts', 'Money spent on things for other external people', NULL),
(10, 'groceries', 'Money spent on grocery store items', NULL),
(11, 'health', 'Things that bring physical or mental well-being and will help us live longer', NULL),
(12, 'house_utilities', 'Money spent on regular house upkeep', NULL),
(13, 'household_goodies', 'Money spent to upgrade our house living', NULL),
(14, 'internet', 'Monthly Plan and Auxillary Purchases', NULL),
(15, 'pharmacy', 'Drug things that need a pharmacist', NULL),
(16, 'phones', 'Money spent on phone plans and auxilary phone items', NULL),
(17, 'rent', 'Money spent on house rent', NULL),
(18, 'social', 'Money spent for activities with other people', NULL),
(19, 'work_expense', 'Money spent because I have a job', NULL),
(20, 'salary', 'Money earned from salary', NULL),
(21, 'side_project', 'Money earned from side projects', NULL),
(22, 'tax_refund', 'Money earned from tax back', NULL),
(23, 'expense_reimbursement', 'Money returned after using benefits on something', NULL),
(24, 'other_earnings', 'Money earned from other sources', NULL),
(25, 'transfer_between_accounts', 'Money that is simply transferred between accounts', NULL),
(26, 'PENDING', 'Category is currently undecided', NULL),
(27, 'banking', 'Fees associated with banking and finances', NULL),
(28, 'mortgage', 'Money spent on house mortgage and taxes', NULL),
(29, 'home_maintain', 'Money spent to maintain our house at a livable quality', NULL),
(30, 'home_reno', 'Money spent to renovate parts of the house', NULL),
(31, 'tools', 'Money spent to buy generic tools or supplies', NULL),
(32, 'other', 'Category is something other', NULL),
(33, 'tattoo', 'Money spent on tattoos or its recovery', NULL)
ON CONFLICT DO NOTHING
;



CREATE TABLE IF NOT EXISTS public.budgets (
    id              SERIAL PRIMARY KEY,
    category_id     INTEGER,
    budget          INTEGER,
    updated_month   DATE
)
;



CREATE TABLE IF NOT EXISTS public.accounts (
    number TEXT PRIMARY KEY,
    type TEXT,
    owner TEXT,
    description TEXT,
    initial_amount FLOAT,
    liquidable BOOLEAN,
    source_of_truth TEXT
)
;


--- These are the deprecated amazon items
CREATE TABLE IF NOT EXISTS public.amazon_items (
    id TEXT,
    name TEXT,
    url TEXT,
    shipped_date TEXT,
    price FLOAT,
    quantity BIGINT,
    transaction_id TEXT,
    order_id TEXT,
    category TEXT,
    new_id TEXT 
)
;

CREATE TABLE IF NOT EXISTS public.amazon_transactions (
    id TEXT,
    shipped_date TEXT,
    price TEXT,
    order_id TEXT
)
;

CREATE TABLE IF NOT EXISTS public.amazon_orders (
    id TEXT,
    url TEXT,
    ordered_date TEXT,
    grand_total TEXT,
    total_before_tax FLOAT,
    tax FLOAT
)
;
