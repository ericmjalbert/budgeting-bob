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
            SELECT
                transactions.id,
                accounts.owner || ' ' || accounts.type AS account_alias,
                DATE(transaction_date) AS transaction_date,
                value,
                COALESCE(description_1, '')
                    || ' '
                    || COALESCE(description_2, '') AS description,
                category
            FROM public.transactions
            INNER JOIN public.accounts
                ON accounts.type = account_type
                AND accounts.number = account_number
            WHERE DATE_TRUNC('month', transaction_date) = '{selected_month}'
            ORDER BY transaction_date DESC, transactions.id
        """
        )
        table_rows = db.fetchall()

        db.execute("SELECT category FROM public.categories ORDER BY category")
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
    row_id = request.args.get("id")
    new_category = request.args.get("category")
    clean_category = new_category.lower().strip()

    with Database() as db:
        sql = f"""
            UPDATE public.transactions
            SET category = '{clean_category}'
            WHERE id = '{row_id}';
        """
        db.execute(sql)

    return "nothing"
