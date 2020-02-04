# Overview

This is a heroku web application that will store account transactions and categorize them for proper budgetting.

## Todo list

1. [x] Get Heroku to show a webpage that says only "Hello World"
2. [x] Get Heroku to have a psql database (or something?) and be able to query/write it 
3. [x] Change webpage to show table data
4. [x] See if I can have a scheduled CRON job run on the background. Something simple like adding a new row with the current timestamp
    * Use `heroku addons:open scheduler`
7. [x] Change backend so that any assigned category is automatically applied to similar transactions
8. [ ] Update UI to allow manual Category updates/overwrites
9. [ ] Update UI to show remaining monthly usage per budget category (report page)
10. [ ] Add search and filter commands to the transactions page

## Random TODOs
* I need to figure out how to initialize the list of categories (prob through the `init_db` startup scription?)
* I need to write something that will automatically get the transactions (not csv import)
* Change CRON script to pull transcations from RBC account
