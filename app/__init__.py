import os
import datetime
from flask import Flask
import psycopg2

app = Flask(__name__)
DATABASE_URL = os.environ["DATABASE_URL"]


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
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cursor = conn.cursor()

    # Create the table if it doesn't yet exist
    cursor.execute(gen_create_table_sql())

    # Insert data into table
    cursor.execute(gen_insert_table_sql(data))

    # commit the changes to the database
    conn.commit()

    # close communication with the database
    cursor.close()


def read_from_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cursor = conn.cursor()

    # Get count of rows
    cursor.execute("SELECT COUNT(*) FROM public.log_timestamp")
    return cursor.fetchone()[0]


def gen_website_message(date):
    row_count = read_from_db()

    msg = f"Hello, World! Today is {date}<br/>"
    msg += f"There are currently {row_count} rows in public.log_timestamp\n"
    return msg


@app.route("/")
@app.route("/index")
def index():
    date = datetime.datetime.today()
    print("start write")
    write_to_db(date)
    print("finish write")

    return gen_website_message(date)
