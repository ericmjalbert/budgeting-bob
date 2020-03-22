from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, request

from .auth import login_required
from .db import Database


bp = Blueprint("budgets", __name__)

CURRENT_MONTH = datetime.now().strftime("%Y-%m-%d")


@bp.route("/budgets")
@login_required
def budgets():
    selected_month = request.args.get("selected_month") or CURRENT_MONTH

    with Database() as db:
        db.execute(
            f"""
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
                AND DATE_TRUNC('month', transaction_date) = '{selected_month}'
                AND budget >= 0
            GROUP BY 1, 2
            """
        )
        budget_rows = db.fetchall()

    available_months = get_available_months()

    return render_template(
        "budgets.html",
        rows=budget_rows,
        months=available_months,
        selected_month=datetime.strptime(selected_month, "%Y-%m-%d")
    )


def get_available_months(starting_month=date(2020, 1, 1)):
    """Get a list of all the months from starting_month to the current date.

    This returns a list of date objects for each valid month.
    """

    now = datetime.now().date()
    diff = now - starting_month

    all_days = [starting_month + timedelta(days=i) for i in range(diff.days)]
    month_trunc = [date.replace(day=1) for date in all_days]
    unique_months = list(set(month_trunc))
    ordered_months = sorted(unique_months, reverse=True)

    return ordered_months
