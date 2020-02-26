from flask import Blueprint, render_template, request

from .auth import login_required
from .db import Database


bp = Blueprint("transactions", __name__)


@bp.route("/transactions")
@login_required
def transactions():

    with Database() as db:
        db.execute(
            """
            SELECT
                id,
                account_type,
                account_number,
                transaction_date,
                value,
                COALESCE(description_1, '')
                    || ' '
                    || COALESCE(description_2, '') AS description,
                category
            FROM public.transactions
            ORDER BY transaction_date DESC
        """
        )
        table_rows = db.fetchall()

        db.execute("SELECT category FROM public.categories ORDER BY category")
        category_names = db.fetchall()

    return render_template(
        "transactions.html", rows=table_rows, categories=category_names
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
