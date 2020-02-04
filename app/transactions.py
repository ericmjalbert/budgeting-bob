from flask import Blueprint, render_template

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
                account_type,
                account_number,
                transaction_date,
                value,
                COALESCE(description_1, '')
                    || ' '
                    || COALESCE(description_2, '') AS description,
                category
            FROM public.transactions
            ORDER BY transaction_date
        """
        )
        table_rows = db.fetchall()

        db.execute("SELECT category FROM public.categories ORDER BY category")
        category_names = db.fetchall()

    return render_template(
        "transactions.html", rows=table_rows, categories=category_names
    )
