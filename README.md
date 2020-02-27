# Overview

This is a heroku web application that will store account transactions and categorize them for proper budgetting.

## Todo list

1. [x] Get Heroku to show a webpage that says only "Hello World"
2. [x] Get Heroku to have a psql database (or something?) and be able to query/write it 
3. [x] Change webpage to show table data
4. [x] See if I can have a scheduled CRON job run on the background. Something simple like adding a new row with the current timestamp
    * Use `heroku addons:open scheduler`
7. [x] Change backend so that any assigned category is automatically applied to similar transactions
8. [x] Update UI to allow manual Category updates/overwrites
9. [ ] Update UI to show remaining monthly usage per budget category (report page)
10. [ ] Update UI to show account totals over time
11. [ ] Add search and filter commands to the transactions page

## Random TODOs
* I need to figure out how to initialize the list of categories (prob through the `init_db` startup scription?)
* I need to write something that will automatically get the transactions (not csv import)
* Change CRON script to pull transcations from RBC account


## Cindy

[x] Change category 'others' to be 'other_earning'
[ ] Need budget page to have a date selection
[ ] Account names to transactions since numbers are not descriptive
[x] Make a category for PENDING
[x] Change games to be "entertainment" (for webtoons and such)
[x] Figure out Cindy BUG with presto
[x] Figure out what's wrong the budget
[x] Category names should appear captialized in the dropdown
[ ] Get the updated column to work whenever someone "SAVES" a transaction category
