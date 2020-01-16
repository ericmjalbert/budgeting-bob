from flask import Blueprint, render_template

from .auth import login_required
from .db import Database


bp = Blueprint("transactions", __name__)


@bp.route("/transactions")
@login_required
def transactions():

    with Database() as db:
        db.execute("SELECT * FROM public.log_timestamp")
        table_rows = db.fetchall()

    return render_template("transactions.html", rows=table_rows)
