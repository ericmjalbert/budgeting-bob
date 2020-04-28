# Main Feature TODOs

1. [x] Get Heroku to show a webpage that says only "Hello World"
2. [x] Get Heroku to have a psql database (or something?) and be able to query/write it 
3. [x] Change webpage to show table data
4. [x] See if I can have a scheduled CRON job run on the background. Something simple like adding a new row with the current timestamp
    * Use `heroku addons:open scheduler`
7. [x] Change backend so that any assigned category is automatically applied to similar transactions
8. [x] Update UI to allow manual Category updates/overwrites
9. [x] Update UI to show remaining monthly usage per budget category (report page)
10. [ ] Update UI to show account totals over time with a visualiation for high-level overview of wealth.
11. [ ] Add search and filter commands to the transactions page
12. [ ] Setup database initialization to not contain private information (Account information)
13. [ ] Setup automated selenium scrapper for RBC to work on Heroku

## Workflow TODOs 
[ ] How do we figure out if something's been miscategorized.
[ ] Need to figure out an easy way to get Amazon categories.
[ ] Need all budget categories to appear on the budget page. Even if there has been NO transactions for a given budget in the selected month.
[ ] Be able to click on the category in "Budget" and have a filtered view of all the transactions with that category.
[ ] Make different levels of "over/under" budget to help process better.
[ ] Setup a logging method to track how category budgets change overtime. If we do a manual change tot he budgets, we should have a log of it so it doesn't break past reports.
