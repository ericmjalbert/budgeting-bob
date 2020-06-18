from flask import Blueprint, jsonify, render_template, request

from .auth import login_required
from .db import Database


bp = Blueprint("account_totals", __name__)


@bp.route("/account_totals")
@login_required
def account_totals():
    return render_template("account_totals.html")


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
