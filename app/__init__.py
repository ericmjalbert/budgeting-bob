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


@app.route("/")
@app.route("/index")
def index():
    date = datetime.datetime.today()
    print("start write")
    write_to_db(date)
    print("finish write")
    return f"Hello, World! Today is {date}"
