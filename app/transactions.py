from datetime import datetime
from flask import Blueprint, render_template, request

from .auth import login_required
from .date import CURRENT_MONTH, get_available_months
from .db import Database


bp = Blueprint("transactions", __name__)


@bp.route("/transactions")
@login_required
def transactions():
    selected_month = request.args.get("selected_month") or CURRENT_MONTH

    with Database() as db:
        db.execute(
            f"""
            WITH include_amazon_transactions AS (
                SELECT
                    transactions.*
                    , ai.id AS amazon_item_id
                    , ai.name
                    , ai.price * ai.quantity AS price
                    , ai.quantity
                    , ai.url
                    , ai.order_id
                    , ai.category AS amazon_item_category
                FROM public.transactions
                LEFT JOIN public.amazon_transactions AS at
                    ON at.price::numeric = (-1 * transactions.value)
                    AND abs(DATE_PART('day', at.shipped_date::timestamp- transactions.transaction_date::timestamp)) <= 1
                    AND description_1 LIKE '%amazon%'
                LEFT JOIN public.amazon_items AS ai
                    ON ai.transaction_id = at.id
            )

            SELECT
                transactions.id,
                accounts.owner || ' ' || accounts.type AS account_alias,
                DATE(transaction_date) AS transaction_date,
                COALESCE(-1 * price, value) AS value,
                COALESCE(description_1, '')
                    || ' '
                    || COALESCE(description_2, '') AS description,
                amazon_item_id,
                url,
                order_id,
                quantity,
                COALESCE(name, '') AS name,
                category,
                amazon_item_category
            FROM include_amazon_transactions AS transactions
            INNER JOIN public.accounts
                ON accounts.type = account_type
                AND accounts.number = account_number
            WHERE DATE_TRUNC('month', transaction_date) = '{selected_month}'
            ORDER BY transaction_date DESC, transactions.id
        """
        )
        table_rows = db.fetchall()

        db.execute("SELECT category FROM public.categories_new ORDER BY category")
        category_names = db.fetchall()

    available_months = get_available_months()

    return render_template(
        "transactions.html",
        rows=table_rows,
        categories=category_names,
        months=available_months,
        selected_month=datetime.strptime(selected_month, "%Y-%m-%d"),
    )


@bp.route("/save_new_category")
@login_required
def save_new_category():
    """Update category on transactions or on amazon_item table.

    Only one of the tables will correspond to the given id, we run the UPDATE
    command on both to avoid having to determine the table from the id.
    """
    row_id = request.args.get("id").strip()
    new_category = request.args.get("category")
    clean_category = new_category.lower().strip()

    with Database() as db:
        sql = f"""
            UPDATE public.transactions
            SET category = '{clean_category}'
            WHERE id = '{row_id}';
        """
        db.execute(sql)

    with Database() as db:
        sql = f"""
            UPDATE public.amazon_items
            SET category = '{clean_category}'
            WHERE id = '{row_id}';
        """
        db.execute(sql)

    return "nothing"
