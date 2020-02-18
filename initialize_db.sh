#!/bin/bash

PSQL=$1

$PSQL -c "
    CREATE TABLE IF NOT EXISTS public.user (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
"

$PSQL -c "
    CREATE TABLE IF NOT EXISTS public.categories (
        category TEXT PRIMARY KEY,
        description TEXT,
        examples TEXT[],
        budget INTEGER
    );
"

# TODO make this properly update so that the hard-coded items here are always true
$PSQL -c "
INSERT INTO public.categories VALUES
('athletics', 'Things that help us be more althetic', ARRAY['skis', 'gym clothings', 'classes'], 200),
('beauty', 'Things for beauty products or services', ARRAY['anything from lush', 'haircuts'], 100),
('car', 'Money spent on things because we have and use the car', ARRAY['gas', 'repairs'], 400),
('cats', 'Things for the cats well-being', ARRAY['food', 'vet'], 200),
('clothing', 'Items what we wear for the purpose of fashion or weather', ARRAY['Coats'], 200),
('dates', 'Money spent for date night activities or dinner', NULL, 300),
('eating', 'Money spent on food for a single person', ARRAY['starbucks', 'work lunch', 'fast food'], 200),
('groceries', 'Money spent on grocery store items', NULL, 750),
('health', 'Things that bring physical or mental well-being and will help us live longer', ARRAY['messages', 'therapy', 'physio'], 300),
('pharmacy', 'Drug things that need a pharmacist', ARRAY['not bandaids', 'not advil', 'birth control'], 50),
('social', 'Money spent for activities with other people', ARRAY['going out with friends'], 200),
('rent', 'Money spent on house rent', NULL, 1800),
('phones', 'Money spent on phone plans and auxilary phone items', ARRAY['Phone Chargers', 'Cases', 'New Phones'], 200),
('internet', 'Monthly Plan and Auxillary Purchases', ARRAY['Routers', 'Modems'], 80),
('house_utilities', 'Money spent on regular house upkeep', ARRAY['hydro', 'gas', 'water'], 250),
('household_goodies', 'Money spent to upgrade our house living', ARRAY['lights', 'vaccum', 'dishes'], 150),
('work_expense', 'Money spent because I have a job', ARRAY['commute'], 500),
('games', 'Money spent on games or related', ARRAY['consoles', 'hacks', 'games purchases'], 100),
('gifts', 'Money spent on things for other external people', ARRAY['christmas presents', 'birthday', '\"Just Because\" gifts'], 150),

('salary', 'Money earned from salary', NULL, -7000),
('side_project', 'Money earned from side projects', NULL, 0),
('tax_refund', 'Money earned from tax back', NULL, 0),
('expense_reimbursement', 'Money returned after using benefits on something', NULL, -250),
('other', 'Money earned from other sources', ARRAY['annuity'], -1100),

('transfer_between_accounts', 'Money that is simply transferred between accounts', NULL, 0)

ON CONFLICT DO NOTHING
"
