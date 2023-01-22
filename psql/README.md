# budgeting-bill-psql

The Postgres database for this service is managed by fly.io: https://fly.io/docs/postgres/

This directory is meant to seperately store the fly.toml and other deployment related files so that the repo root directory stays a bit cleaner.

## Deployment

This should not be needed as part of the regular workflow, but if a deployment for the postgres database is needed you can run regular `flyctl` commands from within this directory and it will read the fly.toml correctly.

The below command will do a typical deployment and will cause a light outage as the new service restarts and becomes healthy.

```
fly deploy .  --app budgeting-bill-psql --image flyio/postgres:14.4
```

## Database Initilization

This whole service is running on the fly.io cloud platform.
This is setup by manually running all the `initialize_*.sh` files, which creates the tables and views.
This can be done from within the `psql/` (So that the proper `fly.toml` is used) directory with:
```
cd psql

flyctl postgres connect -f psql/create_tables.sql
flyctl postgres connect -f psql/create_views.sql
```

For initializing the production data: copy the `setup_dev_dummy_data.sql` insert queryies and write yourself a `setup_prd_data.sql` that inserts the sensitive information.
This should also be run manually.

## Local database

For local development, we create a new docker database and populate it with the dummy data.
This is automatically setup when docker-compose is used.
It uses the same `create_*.sql` files but also runs the `psql/copy_dev_transactions.sql` script to do inserts for dev transactions.

The CSV data is generated from the `generate_dev_data.sql` script.
Running the SQL from that script manually on the production `budgeting-bill-psql` server will create a CSV file that is on the server machine.
This CSV can be SFTP'd back into local machine (and then commited into the repo) with:
```
flyctl ssh sftp shell
get dev_data.csv
```
