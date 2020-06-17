from flask import Blueprint, render_template, request

from .auth import login_required
from .db import Database


bp = Blueprint("account_totals", __name__)


@bp.route("/account_totals")
@login_required
def account_totals():
    return render_template("account_totals.html")
