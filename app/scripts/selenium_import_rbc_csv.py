import os
import time

import hashlib
import click

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    ElementNotVisibleException,
    NoSuchElementException,
)
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

from flask.cli import with_appcontext
import pandas as pd

from app.db import PandasConnection
import app  # noqa # pylint: disable=unused-import

SLEEP_TIME = 1


def get_security_questions(owner):
    security_questions = {
        os.getenv(f"RBC_{owner}_Q1"): os.getenv(f"RBC_{owner}_A1"),
        os.getenv(f"RBC_{owner}_Q2"): os.getenv(f"RBC_{owner}_A2"),
        os.getenv(f"RBC_{owner}_Q3"): os.getenv(f"RBC_{owner}_A3"),
    }

    return security_questions


def try_click(driver, selenium_func, args):
    """This contains the try-except logic for doing selenium clicks."""
    try:
        elem = getattr(driver, selenium_func)(args)
        elem.click()
    except ElementClickInterceptedException:
        # Try clicking a second time
        elem = getattr(driver, selenium_func)(args)
        elem.click()
    except (
        NoSuchElementException,
        ElementNotInteractableException,
        ElementNotVisibleException,
    ):
        time.sleep(SLEEP_TIME)


def initialize_headless_chrome():
    # initialize driver object and change the default download directory
    cwd = os.getcwd()
    chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": cwd}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    return driver


def navigate_rbc_home_page(driver):
    driver.get("https://www.rbc.com")
    time.sleep(3)
    elem = driver.find_element_by_id("header-sign-in-btn")
    elem.click()


def navigate_rbc_login_page(driver, owner):
    username = os.getenv(f"RBC_{owner}")
    password = os.getenv(f"RBC_{owner}_PASS")
    security_questions = get_security_questions(owner)

    # 2. Sign in using environment vars
    elem = driver.find_element_by_id("K1")
    elem.send_keys(username)
    elem = driver.find_element_by_xpath("//input[@type = 'password']")
    elem.send_keys(password)
    elem = driver.find_element_by_xpath("//button[@type = 'submit']")
    elem.click()

    # try to enter security_questions answers if they ask
    try:
        time.sleep(2)
        elem = driver.find_element_by_class_name("pvq-label")
        question_text = elem.text
        answer_to_use = security_questions[question_text]

        elem = driver.find_element_by_class_name("rbc-input")
        elem.send_keys(answer_to_use)
        time.sleep(1)

        elem = driver.find_element_by_class_name("pvq-button")
        elem.click()

    except (NoSuchElementException, ElementNotInteractableException):
        time.sleep(2)

    # Try to accept the "re-enter all your security questions and answers"
    try:
        time.sleep(2)
        elem = driver.find_element_by_id("id_btn_thatwasme")
        elem.click()
        elem = driver.find_element_by_class_name("bodyLink")
        elem.click()
        elem = driver.find_element_by_id("id_btn_continue")
        elem.click()

        # Update persoanl verification questions to the same answer they were before
        for i in [1, 2, 3]:
            elem = Select(driver.find_element_by_id(f"pvqlist{i}"))
            question = [
                dropdown_item.text
                for dropdown_item in elem.options
                if dropdown_item.text in security_questions.keys()
            ][0]
            elem.select_by_visible_text(question)
            elem = driver.find_element_by_id(f"answer{i}")
            elem.send_keys(security_questions[question])

        elem = driver.find_element_by_id("id_btn_continue")
        elem.click()

        # update to pvq confirmation
        elem = driver.find_element_by_class_name("bodyLink")
        elem.click()
    except (
        NoSuchElementException,
        ElementNotInteractableException,
        ElementNotVisibleException,
    ):
        time.sleep(2)


def navigate_rbc_account_summary(driver):
    """Close any modals and click to documents page."""

    # close possible modals
    try_click(driver, "find_element_by_id", "modalWindowCloseButton")
    try_click(driver, "find_element_by_xpath", "//button[@aria-label='Close onboarding modal window']")

    time.sleep(3)

    # Try clicking on Payment history page
    try_click(driver, "find_element_by_xpath", "//a[@rbcportalsubmit = 'AS_Payement_History']")
    try_click(driver, "find_element_by_xpath", "//a[@ga-event-label = 'Account Services']")
    try_click(driver, "find_element_by_xpath", "//a[@title = 'Download Transactions']")


def navigate_rbc_download_page(driver):
    """Click select specific CSV download settings."""
    elem = driver.find_element_by_id("Excel")
    elem.click()

    elem = Select(driver.find_element_by_id("transactionDropDown"))
    elem.select_by_index(1)

    # 4. Save that csv and then run the usual csv import script
    elem = driver.find_element_by_id("id_btn_continue")
    elem.click()
    print("Downloading file")
    time.sleep(2)


def download_csv_from_rbc(owner):

    driver = initialize_headless_chrome()
    driver.get("https://www.rbc.com")

    navigate_rbc_home_page(driver)
    navigate_rbc_login_page(driver, owner)
    navigate_rbc_account_summary(driver)
    navigate_rbc_download_page(driver)

    driver.close()

    cwd = os.getcwd()
    csv_filename = max(
        [f"{cwd}/{f}" for f in os.listdir(cwd) if not f.startswith(".")],
        key=os.path.getctime,
    )
    print(f"Downloaded {csv_filename}")

    return csv_filename


def load_csv(filename):
    df = pd.read_csv(filename, index_col=False)
    return df


def rbc_csv_cleaner(original_df):
    df = original_df.copy()
    df = df.drop("Cheque Number", axis=1)
    df = df.drop("USD$", axis=1)

    df = df.rename(
        columns={
            "Account Type": "account_type",
            "Account Number": "account_number",
            "Transaction Date": "transaction_date",
            "Description 1": "description_1",
            "Description 2": "description_2",
            "CAD$": "value",
        }
    )

    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["description_1"] = df["description_1"].str.lower()
    df["description_2"] = df["description_2"].str.lower()

    df["category"] = None
    df["created"] = pd.Timestamp.now()
    df["updated"] = df["created"]
    df["id"] = (
        df[["account_number", "transaction_date", "description_1", "value"]]
        .astype(str)
        .apply("".join, axis=1)
        .apply(lambda x: hashlib.sha256(x.encode()).hexdigest())
    )

    df = df[
        [
            "id",
            "account_type",
            "account_number",
            "transaction_date",
            "category",
            "value",
            "description_1",
            "description_2",
            "created",
            "updated",
        ]
    ]
    return df


def apply_existing_categories(original_df):
    df = original_df.copy()
    with PandasConnection() as db:
        if True or db.has_table("transactions"):
            categories = pd.read_sql(
                """
                SELECT DISTINCT
                    description_1,
                    FIRST_VALUE(category)
                        OVER (PARTITION BY description_1 ORDER BY updated) AS category
                FROM public.transactions
                WHERE category IS NOT NULL
                """,
                con=db.connect(),
            )
            new_df = df.merge(
                categories, on="description_1", how="left", suffixes=("", "_y")
            )
            new_df["category"] = new_df["category_y"]
            new_df = new_df.drop("category_y", axis=1)
            df = new_df
    return df


def write_df_to_database(df):
    """Removes the existing rows so we don't have duplicates."""
    df = df.set_index("id")
    with PandasConnection() as db:
        existing_ids = pd.read_sql(
            "SELECT id FROM public.transactions", con=db.connect()
        )
        df = df[~df.index.isin(existing_ids["id"])]

        print(f"Writing {len(df)} rows to db")
        df.to_sql(
            name="transactions", schema="public", con=db.connect(), if_exists="append"
        )


@click.command("import-rbc-csv")
@click.argument("owner")
@with_appcontext
def main(owner):
    filename = download_csv_from_rbc(owner)

    print(f"Load {filename} as pandas data frame")
    df = load_csv(filename)

    # Clean up columns
    print("Munge df into format")
    df = rbc_csv_cleaner(df)

    # Query the existing table and join on the description to get existing
    #   categories and add the metadata
    print("Apply existing categories")
    df = apply_existing_categories(df)

    # Write rows to DB, making sure that (account Number, Transaction Date,
    #   CAD$) is the unique key that is used for upserts
    write_df_to_database(df)


if __name__ == "__main__":
    main(owner=None)
