import os
from flask import Flask

from . import auth
from . import time_logs


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev", DATABASE_URL=os.environ["DATABASE_URL"])

    app.register_blueprint(time_logs.bp)
    app.register_blueprint(auth.bp)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    return app
