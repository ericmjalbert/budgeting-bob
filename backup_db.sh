#!/bin/bash

# Use the DATABASE_URL from `heroku config --app budgeting-bob`
PSQL_URL=$1

pg_dump -Fc $PSQL_URL > budgeting-bob.dump

# To restore just run the following and let the errors/warnings play out:
# pg_restore -d $PSQL_URL budgeting-bob.dump
