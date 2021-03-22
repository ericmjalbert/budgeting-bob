from datetime import date, datetime, timedelta
from flask import Blueprint, jsonify, render_template, request

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
            SELECT
                cb.category,
                ROUND(mr.budget::NUMERIC, 2) AS budget,
                ROUND(mr.remaining::NUMERIC, 2) AS remaining,
                ROUND((cb.budget - cs.spend)::NUMERIC, 2) AS overage,
                COALESCE(mr.status, 'Under Budget') AS status,
                COALESCE(mr.status_class, 'table-success') AS status_class
            FROM public.cumulative_budget AS cb
            LEFT JOIN public.cumulative_spend AS cs
                USING (category, month)
            LEFT JOIN public.monthly_remaining AS mr
                USING (category, month)
            WHERE month = '{selected_month}'
                AND mr.budget IS NOT NULL
            ORDER BY 1
            """
        )
        budget_rows = db.fetchall()

        total = {
            "budget": sum([row["budget"] for row in budget_rows]),
            "remaining": sum([row["remaining"] for row in budget_rows]),
            "overage": sum([row["overage"] for row in budget_rows]),
        }

    available_months = get_available_months()

    return render_template(
        "budgets.html",
        rows=budget_rows,
        total=total,
        months=available_months,
        selected_month=datetime.strptime(selected_month, "%Y-%m-%d"),
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


@bp.route("/save_new_budget")
@login_required
def save_new_category():
    """Inserts or update budget value for the current month."""
    category = request.args.get("category").lower().strip()
    new_value = request.args.get("new_value")

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
            WHERE updated_month = '{CURRENT_MONTH}'
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
                    AND updated_month = '{CURRENT_MONTH}';
            """
            db.execute(sql)

        # Insert if it does not exist yet
        else:
            sql = f"""
                INSERT INTO public.budgets (category_id, budget, updated_month)
                VALUES ({category_id}, {new_value}, '{CURRENT_MONTH}')
            """
            db.execute(sql)

    selected_month = request.args.get("selected_month") or CURRENT_MONTH
    return calculate_new_values(category, selected_month)


def calculate_new_values(category, selected_month):
    """Recalculates the budget summary row as a result of the updated budget."""

    with Database() as db:
        sql = f"""
            SELECT
                cb.category,
                ROUND(mr.budget::NUMERIC, 2) AS budget,
                ROUND(mr.remaining::NUMERIC, 2) AS remaining,
                ROUND((cb.budget - cs.spend)::NUMERIC, 2) AS overage,
                COALESCE(mr.status, 'Under Budget') AS status,
                COALESCE(mr.status_class, 'table-success') AS status_class
            FROM public.cumulative_budget AS cb
            LEFT JOIN public.cumulative_spend AS cs
                USING (category, month)
            LEFT JOIN public.monthly_remaining AS mr
                USING (category, month)
            WHERE month = '{selected_month}'
                AND mr.budget IS NOT NULL
        """
        db.execute(sql)
        budget_rows = db.fetchall()
        rows = {
            row["category"]: {
                "budget": float(row["budget"]),
                "remaining": float(row["remaining"]),
                "overage": float(row["overage"]),
                "status": row["status"],
                "status_class": row["status_class"],
            }
            for row in budget_rows
        }

        total = {
            "budget": float(sum([row["budget"] for row in budget_rows])),
            "remaining": float(sum([row["remaining"] for row in budget_rows])),
            "overage": float(sum([row["overage"] for row in budget_rows])),
        }

    print({"total": total, "budget_rows": rows})
    return jsonify({"total": total, "budget_rows": rows})
