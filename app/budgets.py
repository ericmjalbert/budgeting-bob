from datetime import datetime, timedelta
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from flask import Blueprint, jsonify, render_template, request
from itertools import groupby, accumulate


from .auth import login_required
from .date import get_available_months, get_current_month
from .db import Database


bp = Blueprint("budgets", __name__)


def calculate_budget_status(budget, spend):
    """Gets the string and bootstrap 4 class for each budget status.
    """

    remaining = budget + spend
    if remaining < -1 * budget / 2:
        return {"status": "very over budget", "style": "table-danger"}
    elif remaining < 0:
        return {"status": "over budget", "style": "table-warning"}
    elif remaining >= 0:
        return {"status": "under budget", "style": "table-success"}
    else:
        return False


def calc_cumulative_sum(data, selected_month, num_months=None):
    # Filter out months that are too far back
    if not num_months:
        filtered_data = data
    else:
        start_date = datetime.strptime(selected_month, "%Y-%m-%d")
        cutoff_date = (start_date - relativedelta(months=+num_months)).replace(day=1)
        filtered_data = [
            d for d in data
            if (
                d['month'].date() > cutoff_date.date()
                and d['month'].date() <= start_date.date()
            )
        ]

    # Sort the data by category and month
    sorted_data = sorted(filtered_data, key=lambda x: (x['category'], x['month']))

    # Group the sorted data by category
    grouped_data = groupby(sorted_data, key=lambda x: x['category'])

    # Calculate the cumulative sum for each category
    result = {}
    for category, group in grouped_data:
        cumulative_sum = list(accumulate(item['value'] for item in group))
        result[category] = cumulative_sum[-1]
        if category == 'cats':
            print(result[category], cumulative_sum)

    return result


def budget_queries(selected_month):
    """Calculate each categories budget values with multiple queries."""

    # Get the current budget for this month based on budget table
    with Database() as db:
        db.execute(
            f"""
            SELECT DISTINCT
                cn.category,
                b.category_id,
                LAST_VALUE(b.budget) OVER (
                    PARTITION BY b.category_id
                    ORDER BY b.updated_month
                    RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                ) AS value
            FROM budgets AS b
            INNER JOIN categories_new AS cn
                ON cn.id = b.category_id
            WHERE b.updated_month <= '{selected_month}'
                AND cn.category != 'transfer_between_accounts'
                AND b.budget > 0
            ORDER BY 1
            """
        )
        budget_rows = db.fetchall()
        budgets = {budget["category"] : budget["value"] for budget in budget_rows}


    # Get the current spend for this month based on transaction table
    with Database() as db:
        db.execute(
            f"""
            WITH adjusted_transactions AS (
                SELECT
                    tr.id,
                    tr.category,
                    MAX(tr.value) - SUM(COALESCE(-1 * st.value, 0)) AS value_with_split_removed
                FROM transactions AS tr
                LEFT JOIN split_transactions AS st
                    ON st.transaction_id = tr.id
                WHERE DATE_TRUNC('month', tr.transaction_date) = '{selected_month}'
                GROUP BY 1, 2
            ),

            all_transactions AS (
                SELECT
                    category,
                    value_with_split_removed AS value
                FROM adjusted_transactions
                UNION ALL
                SELECT
                    category,
                    -1 * value
                FROM split_transactions
                WHERE DATE_TRUNC('month', transaction_date) = '{selected_month}'
            )

            SELECT
                category,
                ROUND(SUM(value)::NUMERIC, 2) AS value
            FROM all_transactions
            GROUP BY 1
            ORDER BY 1
            """
        )
        spend_rows = db.fetchall()
        spends = {spend["category"] : spend["value"] for spend in spend_rows}

    # Get the current remaining fort this month based on selected_month's budget
    # and spend transaction table
    remaining = {}
    statuses = {}
    for category, budget in budgets.items():
        remaining[category] = budget
        if category in spends:
            # (since value is stored as a positive)
            remaining[category] -= -1 * spends[category]
        statuses[category] = calculate_budget_status(budget, spends.get(category, 0))

    # Calculate the overage for alltime, 6m, 12m, and 24m
    with Database() as db:
        db.execute(
            f"""
            WITH adjusted_transactions AS (
                SELECT
                    tr.id,
                    tr.transaction_date,
                    tr.category,
                    MAX(tr.value) + SUM(COALESCE(-1 * st.value, 0)) AS value_with_split_removed
                FROM transactions AS tr
                LEFT JOIN split_transactions AS st
                    ON st.transaction_id = tr.id
                WHERE DATE_TRUNC('month', tr.transaction_date) <= '{selected_month}'
                GROUP BY 1, 2, 3
            ),

            all_transactions AS (
                SELECT
                    category,
                    transaction_date,
                    value_with_split_removed AS value
                FROM adjusted_transactions
                UNION ALL
                SELECT
                    category,
                    transaction_date,
                    -1 * value
                FROM split_transactions
                WHERE DATE_TRUNC('month', transaction_date) <= '{selected_month}'
            )

            SELECT
                category,
                DATE_TRUNC('month', transaction_date) AS month,
                ROUND(SUM(value)::NUMERIC, 2) AS value
            FROM all_transactions
            GROUP BY 1, 2
            ORDER BY 1, 2
            """
        )
        monthly_spend_rows = db.fetchall()

    with Database() as db:
        db.execute(
            f"""
            SELECT
                category,
                DATE_TRUNC('month', month) AS month,
                budget AS value
            FROM monthly_budget
            WHERE month <= '{selected_month}'
                AND category != 'transfer_between_accounts'
                AND budget > 0
            ORDER BY 1
            """
        )
        monthly_budget_rows = db.fetchall()

    cumulative_budgets_6m = calc_cumulative_sum(monthly_budget_rows, selected_month, 6)
    cumulative_spend_6m = calc_cumulative_sum(monthly_spend_rows, selected_month, 6)
    overage_6m = {
        category: cumulative_budgets_6m.get(category, 0) + cumulative_spend_6m.get(category, 0)
        for category in budgets.keys()
    }

    cumulative_budgets_12m = calc_cumulative_sum(monthly_budget_rows, selected_month, 12)
    cumulative_spend_12m = calc_cumulative_sum(monthly_spend_rows, selected_month, 12)
    overage_12m = {
        category: cumulative_budgets_12m.get(category, 0) + cumulative_spend_12m.get(category, 0)
        for category in budgets.keys()
    }

    cumulative_budgets_24m = calc_cumulative_sum(monthly_budget_rows, selected_month, 24)
    cumulative_spend_24m = calc_cumulative_sum(monthly_spend_rows, selected_month, 24)
    overage_24m = {
        category: cumulative_budgets_24m.get(category, 0) + cumulative_spend_24m.get(category, 0)
        for category in budgets.keys()
    }

    cumulative_budgets = calc_cumulative_sum(monthly_budget_rows, selected_month)
    cumulative_spend = calc_cumulative_sum(monthly_spend_rows, selected_month)
    overage = {
        category: cumulative_budgets.get(category, 0) + cumulative_spend.get(category, 0)
        for category in budgets.keys()
    }

    formatted_budget_rows = []
    for budget in budget_rows:
        row = {}
        category = budget["category"]
        row["category"] = category
        row["budget"] = budget["value"]
        row["remaining"] = remaining[category]
        row["overage"] = overage[category]
        row["overage_6m"] = overage_6m[category]
        row["overage_12m"] = overage_12m[category]
        row["overage_24m"] = overage_24m[category]
        row["status"] = statuses[category]["status"]
        row["status_class"] = statuses[category]["style"]
        formatted_budget_rows.append(row)

    totals = {
        "budget": sum([row["budget"] for row in formatted_budget_rows]),
        "remaining": sum([row["remaining"] for row in formatted_budget_rows]),
        "overage": sum([row["overage"] for row in formatted_budget_rows]),
        "overage_6m": sum([row["overage_6m"] for row in formatted_budget_rows]),
        "overage_12m": sum([row["overage_12m"] for row in formatted_budget_rows]),
        "overage_24m": sum([row["overage_24m"] for row in formatted_budget_rows]),
    }

    return {"rows": formatted_budget_rows, "total": totals}


@bp.route("/budgets")
@login_required
def budgets():
    selected_month = request.args.get("selected_month") or get_current_month()

    budget_results = budget_queries(selected_month)

    available_months = get_available_months()

    return render_template(
        "budgets.html",
        rows=budget_results["rows"],
        total=budget_results["total"],
        months=available_months,
        selected_month=datetime.strptime(selected_month, "%Y-%m-%d"),
    )


@bp.route("/save_new_budget")
@login_required
def save_new_category():
    """Inserts or update budget value for the current month."""
    category = request.args.get("category").lower().strip()
    new_value = request.args.get("new_value")

    current_month = get_current_month()

    # get category_id of the category
    with Database() as db:
        sql = f"SELECT id FROM public.categories_new WHERE category = '{category}'"
        db.execute(sql)
        category_id = db.fetchone()["id"]

    # see if category_id, updated_month already exists by counting number of rows returned
    with Database() as db:
        sql = f"""
            SELECT *
            FROM public.budgets
            WHERE updated_month = '{current_month}'
                AND category_id = '{category_id}'
        """
        db.execute(sql)
        entry_exists = len(db.fetchall()) > 0

    with Database() as db:
        # Update entry if it already exists
        if entry_exists:
            sql = f"""
                UPDATE public.budgets
                SET budget = {new_value}
                WHERE category_id = {category_id}
                    AND updated_month = '{current_month}';
            """
            db.execute(sql)

        # Insert if it does not exist yet
        else:
            sql = f"""
                INSERT INTO public.budgets (category_id, budget, updated_month)
                VALUES ({category_id}, {new_value}, '{current_month}')
            """
            db.execute(sql)

    selected_month = request.args.get("selected_month") or current_month
    return calculate_new_values(category, selected_month)


def calculate_new_values(category, selected_month):
    """Recalculates the budget summary row as a result of the updated budget."""

    budget_results = budget_queries(selected_month)

    rows = {
        row["category"]: {
            "budget": float(row["budget"]),
            "remaining": float(row["remaining"]),
            "overage": float(row["overage"]),
            "overage_6m": float(row["overage_6m"]),
            "overage_12m": float(row["overage_12m"]),
            "overage_24m": float(row["overage_24m"]),
            "status": row["status"],
            "status_class": row["status_class"],
        }
        for row in budget_results["rows"]
    }

    total = {
        "budget": float(sum([row["budget"] for row in budget_results["rows"]])),
        "remaining": float(sum([row["remaining"] for row in budget_results["rows"]])),
        "overage": float(sum([row["overage"] for row in budget_results["rows"]])),
        "overage_6m": float(sum([row["overage_6m"] for row in budget_results["rows"]])),
        "overage_12m": float(sum([row["overage_12m"] for row in budget_results["rows"]])),
        "overage_24m": float(sum([row["overage_24m"] for row in budget_results["rows"]])),
    }

    return jsonify({"total": total, "budget_rows": rows})
