import psycopg2
from psycopg2.extras import RealDictCursor
import sqlalchemy

from flask import current_app


class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = psycopg2.connect(
            current_app.config["DATABASE_URL"], sslmode="require"
        )
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.conn.close()


# TODO try to figure out a how to combine PandasConnection and Database
class PandasConnection:
    def __init__(self):
        self.engine = None

    def __enter__(self):
        self.engine = sqlalchemy.create_engine(current_app.config["DATABASE_URL"])
        return self.engine

    def __exit__(self, exc_type, exc_value, traceback):
        self.engine.dispose()
