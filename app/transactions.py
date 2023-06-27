from datetime import datetime
from flask import Blueprint, render_template, request

from .auth import login_required
from .date import get_available_months, get_current_month
from .db import Database


bp = Blueprint("transactions", __name__)


def gen_search_clause(term):
    """Creates a series of OR clause to search is term is in the transaction."""
    return f"""
        (account_alias LIKE '%{term}%'
        OR transaction_date_format::TEXT LIKE '%{term}%'
        OR value::TEXT LIKE '%{term}%'
        OR description LIKE '%{term}%'
        OR COALESCE(category, 'none') LIKE '%{term}%')
        """


def generate_transaction_sql(selected_month, search_terms):
    """Creates SQL to get transactions.

    Takes a string selected_month or list of string search_terms and will
    generate the appropriate WHERE clauses to ensure that the transactions
    match what's been requested.
    """

    cte_clauses = f"""
        WITH all_transactions AS (
            SELECT
                transactions.id,
                accounts.owner || ' ' || accounts.type AS account_alias,
                DATE(transaction_date) AS transaction_date_format,
                COALESCE(-1 * value) AS value,
                COALESCE(description_1, '')
                    || ' '
                    || COALESCE(description_2, '') AS description,
                category
            FROM public.transactions
            INNER JOIN public.accounts
                ON accounts.type = account_type
                AND accounts.number = account_number
        ),

        split_transactions AS (
            SELECT
                st.id,
                accounts.owner || ' ' || accounts.type AS account_alias,
                DATE(transaction_date) AS transaction_date,
                COALESCE(value) AS value,
                COALESCE(description_1, '')
                    || ' '
                    || COALESCE(description_2, '') AS description,
                category,
                st.transaction_id
            FROM public.split_transactions AS st
            INNER JOIN public.accounts
                ON accounts.type = account_type
                AND accounts.number = account_number
        ),

        transaction_page_list AS (
            SELECT
                at.id,
                at.account_alias,
                at.transaction_date_format,
                ROUND((MAX(at.value) - SUM(COALESCE(st.value, 0)))::NUMERIC, 2) AS value,
                at.description,
                at.category,
                NULL AS transaction_id
            FROM all_transactions AS at
            LEFT JOIN split_transactions AS st
                ON st.transaction_id = at.id
            GROUP BY 1, 2, 3, 5, 6, 7

            UNION ALL

            SELECT
                id,
                account_alias,
                transaction_date,
                value,
                description,
                category,
                transaction_id
            FROM split_transactions
        )
    """

    where_search = [gen_search_clause(term) for term in search_terms]
    where_month = (
        [f"DATE_TRUNC('month', transaction_date_format) = '{selected_month}'"]
        if selected_month
        else []
    )
    where_clauses = " AND ".join(where_search + where_month)
    where_clause = f"WHERE {where_clauses}" if where_clauses else ""

    order_by_clause = """
        ORDER BY
            transaction_date_format DESC,
            COALESCE(transaction_id, id) DESC,
            id
    """

    query = f"""
        {cte_clauses}

        SELECT transaction_date_format AS transaction_date, * FROM transaction_page_list

        {where_clause}
        {order_by_clause}
    """

    return query


@bp.route("/transactions")
@login_required
def transactions():
    # Pull args from query string
    selected_month = request.args.get("selected_month") or get_current_month()
    search = request.args.get("search")
    if search:
        search_terms = [term.strip() for term in search.split("+")]
        selected_month = ""
    else:
        search_terms = []

    # Query database for transactions
    with Database() as db:
        query = generate_transaction_sql(selected_month, search_terms)

        db.execute(query)
        table_rows = db.fetchall()

        db.execute("SELECT category FROM public.categories_new ORDER BY category")
        category_names = db.fetchall()

    available_months = get_available_months()

    if selected_month:
        month_text = datetime.strptime(selected_month, "%Y-%m-%d")
    else:
        month_text = datetime.strptime("9999-01-01", "%Y-%m-%d")

    return render_template(
        "transactions.html",
        rows=table_rows,
        categories=category_names,
        months=available_months,
        search=search,
        selected_month=month_text,
    )


@bp.route("/save_new_category")
@login_required
def save_new_category():
    """Update category on transactions.

    Only one of the tables will correspond to the given id, we run the UPDATE
    command on both to avoid having to determine the table from the id.
    """
    row_id = request.args.get("id").strip()
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
