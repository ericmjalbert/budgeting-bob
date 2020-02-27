from flask import Blueprint, render_template

from .auth import login_required
from .db import Database


bp = Blueprint("budgets", __name__)


@bp.route("/budgets")
@login_required
def budgets():

    with Database() as db:
        # TODO Change the DATE_TRUNC to be based on a selector
        db.execute(
            """
            SELECT
                category,
                budget,
                budget - (-1 * SUM(value)) AS remaining,
                CASE
                    WHEN budget - (-1 * SUM(value)) < 0 THEN 'Over Budget'
                    WHEN budget - (-1 * SUM(value)) >= 0 THEN 'Under Budget'
                    END AS status,
                -- need this column for bootstrap coloring
                CASE
                    WHEN budget - (-1 * SUM(value)) < 0 THEN 'table-warning'
                    WHEN budget - (-1 * SUM(value)) >= 0 THEN 'table-success'
                    END AS status_class
            FROM public.transactions AS tr
            INNER JOIN public.categories AS ca
                USING (category)
            WHERE category != 'transfer_between_accounts'
                AND DATE_TRUNC('month', transaction_date)
                    = DATE_TRUNC('month', CURRENT_DATE)
                AND budget >= 0
            GROUP BY 1, 2
        """)
        budget_rows = db.fetchall()

    return render_template("budgets.html", rows=budget_rows)
