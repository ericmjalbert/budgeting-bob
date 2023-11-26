from flask import Blueprint, jsonify, render_template, request

from .auth import login_required
from .db import Database


bp = Blueprint("account_totals", __name__)


@bp.route("/account_totals")
@login_required
def account_totals():
    with Database() as db:
        sql = """
            SELECT
                a.owner,
                a.type,
                a.description,
                a.initial_amount + COALESCE(t.value, 0) AS current_total
            FROM accounts AS a
            LEFT JOIN (
                SELECT account_number, SUM(value) AS value FROM transactions GROUP BY 1
            ) AS t
                ON t.account_number = a.number
        """
        db.execute(sql)
        accounts = db.fetchall()

    with Database() as db:
        sql = """
            SELECT
                COALESCE(MAX(transaction_date), '1970-01-01 00:00:00') AS max
            FROM transactions
        """
        db.execute(sql)
        result = db.fetchone()
    latest_transaction = result["max"]

    current_overall_total = sum([account["current_total"] for account in accounts])

    return render_template(
        "account_totals.html",
        latest_transaction=latest_transaction,
        accounts=accounts,
        current_overall_total=current_overall_total,
    )


@bp.route("/get_account_daily_totals")
@login_required
def get_account_daily_totals():
    with Database() as db:
        sql = f"""
            SELECT
                DATE_TRUNC('day', t.transaction_date) AS day,
                SUM(t.value) AS total
            FROM accounts AS a
            INNER JOIN transactions AS t
                ON t.account_number = a.number
            GROUP BY 1
            ORDER BY 1
        """
        db.execute(sql)
        data = db.fetchall()

    cleaned = [
        {"day": row["day"].strftime("%Y-%m-%d"), "total": row["total"]} for row in data
    ]

    cleaned = add_initial_amount_to_first_day(cleaned)

    return jsonify(cleaned)


def add_initial_amount_to_first_day(cleaned):
    with Database() as db:
        sql = f"""
            SELECT SUM(initial_amount) AS total FROM accounts;
        """
        db.execute(sql)
        initial_amount = db.fetchone()

    cleaned[0]["total"] += initial_amount["total"]
    return cleaned


@bp.route("/get_account_initial_amount")
@login_required
def get_account_initial_amount():
    with Database() as db:
        sql = f"""
            SELECT SUM(initial_amount) AS total FROM accounts;
        """
        db.execute(sql)
        data = db.fetchall()

    cleaned = {"total": row["total"] for row in data}
    return jsonify(cleaned)
