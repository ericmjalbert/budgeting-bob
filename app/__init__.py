import os
import random

from flask import Flask

from . import account_totals
from . import auth
from . import budgets
from . import home
from . import transactions
from . import upload_statements


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    random_secret_key = '%030x' % random.randrange(16**30)
    secret_key = "dev" if os.getenv("LOCAL_MODE") else random_secret_key

    app.config.from_mapping(
        SECRET_KEY=secret_key,
        DATABASE_URL=os.environ["DATABASE_URL"],
    )

    app.register_blueprint(account_totals.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(budgets.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(upload_statements.bp)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    return app


my_app = create_app()
