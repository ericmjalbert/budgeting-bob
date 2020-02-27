import hashlib
import click

from flask.cli import with_appcontext
import pandas as pd

from app.db import PandasConnection
import app  # noqa # pylint: disable=unused-import


def load_csv():
    # TODO get this filename from command line
    filename = "app/scripts/csv30374.csv"
    df = pd.read_csv(filename, index_col=False)
    return df


def rbc_csv_cleaner(original_df):
    df = original_df.copy()
    df = df.drop("Cheque Number", axis=1)
    df = df.drop("USD$", axis=1)

    df = df.rename(
        columns={
            "Account Type": "account_type",
            "Account Number": "account_number",
            "Transaction Date": "transaction_date",
            "Description 1": "description_1",
            "Description 2": "description_2",
            "CAD$": "value",
        }
    )

    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["description_1"] = df["description_1"].str.lower()
    df["description_2"] = df["description_2"].str.lower()

    df["category"] = None
    df["created"] = pd.Timestamp.now()
    df["updated"] = df["created"]
    df["id"] = (
        df[["account_number", "transaction_date", "description_1", "value"]]
        .astype(str)
        .apply("".join, axis=1)
        .apply(lambda x: hashlib.sha256(x.encode()).hexdigest())
    )

    df = df[
        [
            "id",
            "account_type",
            "account_number",
            "transaction_date",
            "category",
            "value",
            "description_1",
            "description_2",
            "created",
            "updated",
        ]
    ]
    return df


def apply_existing_categories(original_df):
    df = original_df.copy()
    with PandasConnection() as db:
        if True or db.has_table("transactions"):
            categories = pd.read_sql(
                """
                SELECT DISTINCT description_1, category
                FROM public.transactions WHERE category IS NOT NULL
                """,
                con=db.connect(),
            )
            new_df = pd.merge(
                df, categories, on="description_1", how="left", suffixes=("", "_y")
            )
            new_df["category"] = new_df["category_y"]
            new_df = new_df.drop("category_y", axis=1)
            df = new_df
    return df


def write_df_to_database(df):
    """Removes the existing rows so we don't have duplicates."""
    df = df.set_index("id")
    with PandasConnection() as db:
        existing_ids = pd.read_sql(
            "SELECT id FROM public.transactions", con=db.connect()
        )
        df = df[~df.index.isin(existing_ids["id"])]
        df.to_sql(
            name="transactions", schema="public", con=db.connect(), if_exists="append"
        )


@click.command("import-rbc-csv")
@with_appcontext
def main():
    df = load_csv()

    # Clean up columns
    df = rbc_csv_cleaner(df)

    # Query the existing table and join on the description to get existing
    #   categories and add the metadata
    df = apply_existing_categories(df)

    # Write rows to DB, making sure that (account Number, Transaction Date,
    #   CAD$) is the unique key that is used for upserts
    write_df_to_database(df)


if __name__ == "__main__":
    main()


### REMOVE DUPLICATES
"""
BEGIN;

ALTER TABLE public.transactions ADD COLUMN row_number SERIAL;

CREATE TABLE public.new_transactions AS
WITH ranked AS (
    SELECT id, account_type, account_number, transaction_date, category, value, description_1, description_2, created, updated,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY row_number) AS rank
    FROM public.transactions
)
SELECT id, account_type, account_number, transaction_date, category, value, description_1, description_2, created, updated
FROM ranked
WHERE rank = 1
;

ALTER TABLE public.transactions RENAME TO backup_transactions;
ALTER TABLE public.new_transactions RENAME TO transactions;

COMMIT;

"""
