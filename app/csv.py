import os
import time

import hashlib

import pandas as pd
from app.db import PandasConnection


def load_csv(filename):
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
                SELECT DISTINCT
                    description_1,
                    FIRST_VALUE(category)
                        OVER (
                            ORDER BY transaction_date DESC
                            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                        ) AS category
                FROM public.transactions
                WHERE category IS NOT NULL
                """,
                con=db.connect(),
            )
            new_df = df.merge(
                categories, on="description_1", how="left", suffixes=("", "_y")
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

        print(f"Writing {len(df)} rows to db")
        df.to_sql(
            name="transactions", schema="public", con=db.connect(), if_exists="append"
        )
    return len(df)


def rbc_statement_parser(filename):
    print(f"Load {filename} as pandas data frame")
    df = load_csv(filename)

    # Clean up columns
    print("Munge df into format")
    df = rbc_csv_cleaner(df)

    # Query the existing table and join on the description to get existing
    #   categories and add the metadata
    print("Apply existing categories")
    df = apply_existing_categories(df)

    # Write rows to DB, making sure that (account Number, Transaction Date,
    #   CAD$) is the unique key that is used for upserts
    written_rows = write_df_to_database(df)

    return written_rows
