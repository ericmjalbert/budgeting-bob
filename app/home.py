from flask import Blueprint, render_template

from .auth import login_required

bp = Blueprint("home", __name__, url_prefix="/")


@bp.route("/")
@bp.route("/home")
@login_required
def home():
    return render_template("home.html")
