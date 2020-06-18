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
        rows = db.fetchone()["rows"]
    return rows


def init_user_table():
    with Database() as db:
        sql = """
            CREATE TABLE IF NOT EXISTS public.user (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        """
        db.execute(sql)


def init_categories_table():
    with Database() as db:
        sql = """
            CREATE TABLE IF NOT EXISTS public.categories (
                category TEXT PRIMARY KEY,
                description TEXT,
                budget INTEGER
            );
        """
        db.execute(sql)

        sql = """
        INSERT INTO public.categories VALUES
        ('athletics', 'Things that help us be more althetic', 500),
        ('beauty', 'Things for beauty products or services', 500),
        ('car', 'Money spent on things because we have and use the car', 1000),
        ('cats', 'Things for the cats well-being', 500),
        ('clothing', 'Items what we wear for the purpose of fashion or weather', 500),
        ('dates', 'Money spent for date night activities or dinner', 500),
        ('eating', 'Money spent on food for a single person', 500),
        ('entertainment', 'Money spent on games or other entertaining things', 250),
        ('gifts', 'Money spent on things for other external people', 250),
        ('groceries', 'Money spent on grocery store items', 1000),
        ('health', 'Things for physical/mental well-being', 250),
        ('house_utilities', 'Money spent on regular house upkeep', 250),
        ('household_goodies', 'Money spent to upgrade our house living', 250),
        ('internet', 'Monthly Plan and Auxillary Purchases', 250),
        ('pharmacy', 'Drug things that need a pharmacist', 250),
        ('phones', 'Money spent on phone plans and auxilary phone items', 250),
        ('rent', 'Money spent on house rent', 2000),
        ('social', 'Money spent for activities with other people', 500),
        ('work_expense', 'Money spent because I have a job', 500),

        ('salary', 'Money earned from salary', -10000),
        ('other_earnings', 'Money earned from other sources', 0),

        ('transfer_between_accounts', 'Money that is transferred between accounts', 0),
        ('PENDING', 'Category is currently undecided', 0)

        ON CONFLICT DO NOTHING
        """
        db.execute(sql)


def init_accounts_table():
    with Database() as db:
        sql = """
            CREATE TABLE IF NOT EXISTS public.accounts (
                number TEXT PRIMARY KEY,
                type TEXT,
                owner TEXT,
                description TEXT,
                initial_amount FLOAT,
                liquidable BOOLEAN,
                source_of_truth TEXT
            );
        """
        db.execute(sql)

        sql = """
            INSERT INTO public.accounts VALUES
            ('1111'), 'Savings', 'Bob', 'RBC Banking', 20000, TRUE, 'RBC'),
            ('2222'), 'Visa', 'Bob', 'RBC Rewards VISA', 0, TRUE, 'RBC'),
            ('3333'), 'Savings', 'Bobbette', 'RBC Banking', 50000, TRUE, 'RBC')
            ON CONFLICT DO NOTHING
            ;
        """
        db.execute(sql)


def initialize_database():
    with Database() as db:
        sql = """
        SELECT FROM pg_tables
        WHERE schemaname = 'public'
            AND tablename  = 'user'
        """
        db.execute(sql)
        user_table_exists = (db.rowcount() == 1)

    if not user_table_exists:
        init_user_table()
        init_categories_table()
        init_accounts_table()
