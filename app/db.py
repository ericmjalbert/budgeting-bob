import psycopg2
from psycopg2.extras import RealDictCursor

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


def gen_create_table_sql():
    return """
        CREATE TABLE IF NOT EXISTS public.log_timestamp (
            id SERIAL PRIMARY KEY,
            created TIMESTAMPTZ
        )
    """


def gen_insert_table_sql(data):
    return f"""
        INSERT INTO public.log_timestamp (created)
        VALUES ('{data}');
    """


def write_to_db(data):
    with Database() as db:
        # Create the table if it doesn't yet exist
        db.execute(gen_create_table_sql())

        # Insert data into table
        db.execute(gen_insert_table_sql(data))


def read_from_db():
    with Database() as db:
        # Get count of rows
        db.execute("SELECT COUNT(*) AS rows FROM public.log_timestamp")
        rows = db.fetchone()['rows']
    return rows
