import os
from flask import Flask

from . import account_totals
from . import auth
from . import budgets
from . import home
from . import time_logs
from . import transactions

from .scripts import write_timestamp_row
from .scripts import selenium_import_rbc_csv
from db import initialize_database


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev", DATABASE_URL=os.environ["DATABASE_URL"])

    initialize_database()

    app.register_blueprint(account_totals.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(budgets.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(time_logs.bp)
    app.register_blueprint(transactions.bp)

    app.cli.add_command(write_timestamp_row.write_timestamp)
    app.cli.add_command(selenium_import_rbc_csv.main)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    return app


my_app = create_app()
