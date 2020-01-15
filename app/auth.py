import functools
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import Database

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        # Hard-code username so there can be only 1 user account
        username = "admin_jalbert"
        password = request.form["password"]
        error = None

        with Database() as db:
            if not username:
                error = "Username is required."
            elif not password:
                error = "Password is required."

            db.execute(
                "SELECT EXISTS (SELECT id FROM public.user WHERE username = %s)",
                (username,),
            )
            user_exists = db.fetchone()["exists"]
            if user_exists:
                error = "User {} is already registered.".format(username)

            if error is None:
                db.execute(
                    "INSERT INTO public.user (username, password) VALUES (%s, %s)",
                    (username, generate_password_hash(password)),
                )
                return redirect(url_for("auth.login"))

            flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None
        with Database() as db:
            db.execute(
                "SELECT EXISTS (SELECT id FROM public.user WHERE username = %s)",
                (username,),
            )
            user_exists = db.fetchone()
            if user_exists:
                db.execute("SELECT * FROM public.user WHERE username = %s", (username,))
                user = db.fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("time_logs.index"))

        flash(error)

    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        with Database() as db:
            try:
                db.execute("SELECT * FROM public.user WHERE id = %s", (user_id,))
                user = db.fetchone()["username"]
                g.user = user
            except TypeError:
                g.user = None


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
