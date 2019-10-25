# Overview

This is a heroku web application that will store account transactions and categorize them for proper budgetting.

## Todo list

1. [ ] Get Heroku to show a webpage that says only "Hello World"
2. [ ] Get Heroku to have a psql database (or something?) and be able to query it 
3. [ ] Change webpage to show table data
4. [ ] See if I can have a scheduled CRON job run on the background. Something simple like adding a new row with the current timestamp
5. [ ] See if I can get secrets (rbc password) stored on the server, use them to access the account
6. [ ] Change CRON script to pull transcations from RBC account
7. [ ] Update UI to show summary info on transactions (monthly income/expense)
8. [ ] Create some sort of UI to manually assign categories to transactions
9. [ ] Change backend so that any assigned category is automatically applied to similar transactions
10. [ ] Use some ML to auto assign categories
