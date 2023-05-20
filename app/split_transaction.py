from io import StringIO

from flask import Blueprint, render_template, redirect, request, url_for
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import hashlib
import pandas as pd
import re

from .auth import login_required
from .db import Database


bp = Blueprint("split_transaction", __name__)


def get_transaction(id):
    """Creates SQL to get a single original transaction.
    """

    query = f"""
        SELECT
            transactions.id,
            accounts.owner || ' ' || accounts.type AS account_alias,
            DATE(transaction_date) AS transaction_date,
            COALESCE(-1 * value) AS value,
            COALESCE(description_1, '')
                || ' '
                || COALESCE(description_2, '') AS description,
            category
        FROM public.transactions
        INNER JOIN public.accounts
            ON accounts.type = account_type
            AND accounts.number = account_number
        WHERE transactions.id = '{id}'
    """

    with Database() as db:
        db.execute(query)
        row = db.fetchall()

    return row


def get_split_transaction(id):
    """Creates SQL to get all the split transactions from an original transaction.
    """

    query = f"""
        SELECT
            st.id,
            accounts.owner || ' ' || accounts.type AS account_alias,
            DATE(transaction_date) AS transaction_date,
            COALESCE(value) AS value,
            COALESCE(description_1, '')
                || ' '
                || COALESCE(description_2, '') AS description,
            category
        FROM public.split_transactions as st
        INNER JOIN public.accounts
            ON accounts.type = account_type
            AND accounts.number = account_number
        WHERE st.transaction_id = '{id}'
    """

    with Database() as db:
        db.execute(query)
        row = db.fetchall()

    return row


@bp.route("/split_transaction", methods=["GET", "POST"])
@login_required
def split_transaction():
    id = request.args.get('id')

    transaction = get_transaction(id)[0]

    with Database() as db:
        db.execute("SELECT category FROM public.categories_new ORDER BY category")
        category_names = db.fetchall()

    read_only_rows = get_split_transaction(id)

    split_value = float(transaction["value"])
    for row in read_only_rows:
        split_value -= float(row["value"])

    transaction["value"] = split_value
    return render_template(
        "split_transaction.html",
        row=transaction,
        categories=category_names,
        read_only_rows=read_only_rows,
    )


@bp.route("/delete_split_transaction")
@login_required
def delete_split_transaction():
    """Deletes the given id from the split_transactions table.

    Used in transaction page as the trash icon.
    """
    id = request.args.get("id").strip()

    with Database() as db:
        sql = f"""
            DELETE FROM split_transactions
            WHERE id = '{id}';
        """
        db.execute(sql)
        print(f"Successfully deleted {id} from split_transactions table.")

    return "nothing"


@bp.route("/save_split_transaction")
@login_required
def save_split_transaction():
    """Add new row to split_transaction table.
    """
    original_id = request.args.get("id").strip()

    category = request.args.get("category")
    category = category.lower().strip()

    value = request.args.get("value")

    description_1 = request.args.get("description")
    description_1 = re.sub(r'[^\w\s]', '', description_1)

    original_transaction = get_transaction(original_id)[0]
    account_number = original_transaction["account_alias"]
    transaction_date = original_transaction["transaction_date"]

    id_str = f"{account_number}{transaction_date}{description_1}{value}"
    id = hashlib.sha256(id_str.encode()).hexdigest()

    with Database() as db:
        sql = f"""
            INSERT INTO split_transactions
            SELECT
                '{id}' as id,
                account_type,
                account_number,
                transaction_date,
                '{category}',
                '{value}',
                '{description_1}',
                '',
                '{pd.Timestamp.now()}',
                '{pd.Timestamp.now()}',
                '{original_id}'
            FROM transactions
            WHERE transactions.id = '{original_id}'
        """
        db.execute(sql)
        print(f"Successfully Written {id} to split_transactions table.")

    return "nothing"
