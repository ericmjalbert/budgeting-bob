from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, request

from .auth import login_required
from .db import Database


bp = Blueprint("budgets", __name__)

CURRENT_MONTH = datetime.now().replace(day=1).strftime("%Y-%m-%d")


@bp.route("/budgets")
@login_required
def budgets():
    selected_month = request.args.get("selected_month") or CURRENT_MONTH

    with Database() as db:
        db.execute(
            f"""
            WITH cumulative_budget AS (
                SELECT
                    category,
                    SUM(budget) AS budget
                FROM public.categories
                CROSS JOIN generate_series('2020-01-01', CURRENT_DATE, '1 month')
                WHERE budget >= 0
                GROUP BY 1
            ),

            cumulative_spending AS (
                SELECT
                    category,
                    SUM(-1 * value) AS spend
                FROM public.transactions
                WHERE transaction_date > '2020-01-01'
                    AND category != 'transfer_between_accounts'
                GROUP BY 1
            ),

            specific_month_remaining AS (
                SELECT
                    category,
                    ca.budget,
                    ca.budget - (-1 * SUM(tr.value)) AS remaining,
                    CASE
                        WHEN ca.budget - (-1 * SUM(tr.value)) < 0 THEN 'Over Budget'
                        WHEN ca.budget - (-1 * SUM(tr.value)) >= 0 THEN 'Under Budget'
                        END AS status,
                    -- need this column for bootstrap coloring
                    CASE
                        WHEN ca.budget - (-1 * SUM(tr.value)) < 0 THEN 'table-warning'
                        WHEN ca.budget - (-1 * SUM(tr.value)) >= 0 THEN 'table-success'
                        END AS status_class
                FROM public.transactions AS tr
                INNER JOIN public.categories AS ca
                    USING (category)
                WHERE category != 'transfer_between_accounts'
                    AND DATE_TRUNC('month', tr.transaction_date) = '{selected_month}'
                    AND ca.budget >= 0
                GROUP BY 1, 2
            )

            SELECT
                category,
                smr.budget,
                ROUND(smr.remaining::NUMERIC, 2) AS remaining,
                ROUND(cb.budget - cs.spend::NUMERIC, 2) AS overage,
                smr.status,
                smr.status_class
            FROM specific_month_remaining AS smr
            INNER JOIN cumulative_budget AS cb
                USING (category)
            INNER JOIN cumulative_spending AS cs
                USING (category)
            ORDER BY 1
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
