# budgeting-bill-psql

The Postgres database for this service is managed by fly.io: https://fly.io/docs/postgres/

This directory is meant to seperately store the fly.toml and other deployment related files so that the repo root directory stays a bit cleaner.

## Deployment

**This should not be needed as part of the regular workflow**.
However, if a deployment for the postgres database is needed you can run regular `flyctl` commands from within this directory and it will read the fly.toml correctly.

The below command will do a typical deployment and will cause a light outage as the new service restarts and becomes healthy.

```
fly deploy .  --app budgeting-bill-psql --image flyio/postgres:14.4
```

## Database Initilization

This whole service is running on the fly.io cloud platform.
This is setup by manually running the `create_tables.sql` and then `create_views.sql` files.
This can be done from within the `psql/` (So that the proper `fly.toml` is used) directory with:
```
cd psql

flyctl postgres connect -f psql/create_tables.sql
flyctl postgres connect -f psql/create_views.sql
```

For initializing the production data, copy the `setup_dev_dummy_data.sql` queries and write yourself a `setup_prd_data.sql` that inserts the sensitive information.
This file should not be commited to version control.
This should also be run manually.

## Local database

For local development, we create a new docker database and populate it with the dummy data.
This is automatically setup when docker-compose is used.
It uses the same `create_*.sql` files but also runs the `psql/setup_dev_dummy_data.sql` script to do inserts for dev transactions.
