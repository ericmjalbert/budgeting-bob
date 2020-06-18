#!/bin/bash

PSQL="heroku pg:psql --app budgeting-bob-demo"

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
        budget INTEGER
    );
"

# TODO make this properly update so that the hard-coded items here are always true
$PSQL -c "
    INSERT INTO public.categories VALUES
    ('athletics', 'Things that help us be more althetic', 500),
    ('beauty', 'Things for beauty products or services', 500),
    ('car', 'Money spent on things because we have and use the car', 1000),
    ('cats', 'Things for the cats well-being', 500),
    ('clothing', 'Items what we wear for the purpose of fashion or weather', 500),
    ('dates', 'Money spent for date night activities or dinner', 500),
    ('eating', 'Money spent on food for a single person', 500),
    ('entertainment', 'Money spent on games or other entertaining things', 250),
    ('gifts', 'Money spent on things for other external people', 250),
    ('groceries', 'Money spent on grocery store items', 1000),
    ('health', 'Things for physical/mental well-being', 250),
    ('house_utilities', 'Money spent on regular house upkeep', 250),
    ('household_goodies', 'Money spent to upgrade our house living', 250),
    ('internet', 'Monthly Plan and Auxillary Purchases', 250),
    ('pharmacy', 'Drug things that need a pharmacist', 250),
    ('phones', 'Money spent on phone plans and auxilary phone items', 250),
    ('rent', 'Money spent on house rent', 2000),
    ('social', 'Money spent for activities with other people', 500),
    ('work_expense', 'Money spent because I have a job', 500),

    ('salary', 'Money earned from salary', -10000),
    ('other_earnings', 'Money earned from other sources', 0),

    ('transfer_between_accounts', 'Money that is transferred between accounts', 0),
    ('PENDING', 'Category is currently undecided', 0)

    ON CONFLICT DO NOTHING
"

$PSQL -c "
CREATE TABLE IF NOT EXISTS public.accounts (
    number TEXT PRIMARY KEY,
    type TEXT,
    owner TEXT,
    description TEXT,
    initial_amount FLOAT,
    liquidable BOOLEAN,
    source_of_truth TEXT
);
"

$PSQL -c "
    INSERT INTO public.accounts VALUES
    ('1111', 'Savings', 'Bob', 'RBC Banking', 20000, TRUE, 'RBC'),
    ('2222', 'Visa', 'Bob', 'RBC Rewards VISA', 0, TRUE, 'RBC'),
    ('3333', 'Savings', 'Bobbette', 'RBC Banking', 50000, TRUE, 'RBC'),
    ('4444', 'Visa', 'Bobbette', 'RBC Platinum VISA', 0, TRUE, 'RBC')
    ON CONFLICT DO NOTHING
    ;
"
