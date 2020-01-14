import datetime
from flask import Blueprint, render_template

from .db import read_from_db, write_to_db


def gen_website_message(date):
    row_count = read_from_db()

    msg = f"Hello, World! Today is {date}<br/>"
    msg += f"There are currently {row_count} rows in public.log_timestamp\n"
    return msg


bp = Blueprint("time_logs", __name__, url_prefix="/")


@bp.route("/index")
def index():
    date = datetime.datetime.today()
    write_to_db(date)

    return render_template("time_logs.html", msg_content=gen_website_message(date))
