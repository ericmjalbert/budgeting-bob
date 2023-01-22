from io import StringIO

from flask import Blueprint, render_template, redirect, request, url_for
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage


from .auth import login_required
from .csv import rbc_statement_parser


bp = Blueprint("upload_statements", __name__)


@bp.route("/upload_statements", methods=["GET", "POST"])
@login_required
def upload_statements():
    rows_written = None
    filename = None
    if request.method == 'POST':
        uploaded_file = request.files['csv']
        print("uploaded filename is: ", uploaded_file.filename)

        if uploaded_file.filename != '':
            uploaded_file.save(uploaded_file.filename)
            print("successfully saved CSV")
            rows_written = rbc_statement_parser(uploaded_file.filename)
            print(f"Written {rows_written} rows to DB")
        filename = uploaded_file.filename

    return render_template(
        "upload_statements.html",
        filename=filename,
        rows_written=rows_written,
    )
