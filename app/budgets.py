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
                    WHEN SUM(value) > budget THEN 'over_budget'
                    WHEN SUM(value) < budget THEN 'under_budget'
                    END AS status
            FROM public.transactions AS tr
            INNER JOIN public.categories AS ca
                USING (category)
            WHERE DATE_TRUNC('m', transaction_date) = DATE_TRUNC('m', CURRENT_DATE-30)
                AND budget >= 0
            GROUP BY 1, 2
        """)
        budget_rows = db.fetchall()

    return render_template("budgets.html", rows=budget_rows)
