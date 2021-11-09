from dataclasses import dataclass
import math
import os
import time
from typing import List
from urllib.parse import urlparse
from urllib.parse import parse_qs
import uuid

import hashlib
import click
import dateparser

from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    ElementNotVisibleException,
    NoSuchElementException,
)
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

from psycopg2.errors import UndefinedTable
from sqlalchemy.exc import ProgrammingError

from flask.cli import with_appcontext
import pandas as pd

from app.db import PandasConnection
import app  # noqa # pylint: disable=unused-import


CDN_TAX = 1.13


@dataclass
class Order:
    id: str
    url: str
    ordered_date: str
    grand_total: float
    total_before_tax: float = 0
    tax: float = 0


@dataclass
class Transaction:
    id: str
    shipped_date: str
    price: float = None
    order_id: str = None


@dataclass
class Item:
    id: str
    name: str
    url: str
    shipped_date: str
    price: float
    quantity: int
    transaction_id: str = None
    order_id: str = None


def gen_primary_key(seed):
    """Generates a unique primary key based on the given seed.

    If a duplicate seed if given at a later time, the data will correctly be
    identified as a duplicate since the primary key will be the same.
    """
    return str(uuid.uuid5(namespace=uuid.NAMESPACE_URL, name=seed))


def normalize_datestr(datestr) -> str:
    """Converts the datestr into a normalized format YYYY-MM-DD."""
    return dateparser.parse(datestr).strftime("%Y-%m-%d")


def get_order_id_from_url(current_url) -> str:
    cleaned_url = urlparse(current_url)
    order_id = parse_qs(cleaned_url.query)["orderID"][0]
    return order_id


def write_df_to_database(df, tablename):
    """Removes the existing rows so we don't have duplicates."""
    df = df.set_index("id")
    with PandasConnection() as db:
        try:
            existing_ids = pd.read_sql(
                f"SELECT id FROM public.{tablename}", con=db.connect()
            )
            df_only_new = df[~df.index.isin(existing_ids["id"])]
        except ProgrammingError:
            df_only_new = df

        print(f"Writing {len(df_only_new)} rows to db")
        df_only_new.to_sql(
            name=tablename, schema="public", con=db.connect(), if_exists="append"
        )


def initialize_headless_chrome():
    # initialize driver object and change the default download directory
    driver = webdriver.Chrome(ChromeDriverManager().install())

    return driver


def amazon_sign_in(driver):
    # Sometimes it'll ask for my cellphone number; skip this page
    try:
        elem = driver.find_element_by_id("ap-account-fixup-phone-skip-link")
        elem.click()
    except NoSuchElementException:
        pass

    # email page
    try:
        elem = driver.find_element_by_name("email")
        elem.send_keys("ericmjalbert@gmail.com")

        elem = driver.find_element_by_id("continue")
        elem.click()
    except ElementNotInteractableException:
        print("email is already entered")
        pass

    # password page
    elem = driver.find_element_by_name("password")
    elem.send_keys(os.getenv("AMAZON_SIGNIN_PASSWORD"))

    elem = driver.find_element_by_id("signInSubmit")
    elem.click()

    return


def get_order_urls(driver) -> List[str]:

    time.sleep(1)
    # Now I'm on order page and I'm going to change the date range filter
    elem = driver.find_element_by_xpath(
        "//span[@data-a-class = 'order-filter-dropdown']"
    )
    elem.click()
    elem = elem.find_element_by_xpath(
        "//a[contains(text(), 'past 3 months')]"
    )  # this should be '2021', dynamic, or maybe the "past 3 months" value?
    elem.click()

    order_urls = []
    while True:
        # Now I'm going to get all the orders
        elem = driver.find_element_by_id("ordersContainer")

        # this is all the orders on this page
        elems = elem.find_elements_by_class_name("order")

        for order_card in elems:
            try:
                elem = order_card.find_element_by_xpath(
                    ".//a[contains(@href, '/gp/your-account/order-details')]"
                )
                order_urls.append(elem.get_attribute("href"))
            except NoSuchElementException:
                elem = order_card.find_element_by_xpath(
                    ".//a[contains(@href, '/gp/digital/your-account/')]"
                )
                order_urls.append(elem.get_attribute("href"))
        print(order_urls)

        # Go to the nexst page and get more orders
        try:
            elem = driver.find_element_by_class_name("a-pagination")
            elem = elem.find_element_by_class_name("a-last")
            if "a-disabled" not in elem.get_attribute("class"):
                elem.click()
            else:
                print("There are no more pages to navigate through")
                break
        except NoSuchElementException:
            print("There is only one page to navigate")
            break
    return order_urls


def get_book_transaction(driver) -> Transaction:
    """Reads the transaction information from a digital book order.

    These types of orders have a different format compared to regular amazon orders.
    """

    elem = driver.find_element_by_xpath("//*[contains(text(), 'Digital Order:')]")
    shipped_date_text = elem.text.split("Digital Order: ")[1]
    shipped_date = normalize_datestr(shipped_date_text)

    elem = driver.find_element_by_class_name("pmts-grand-order-total")
    price = elem.find_element_by_xpath(".//span[contains(text(), '$')]").text.replace(
        "$", ""
    )
    print(shipped_date, price)

    id = gen_primary_key(f"{shipped_date}{price}")
    order_id = get_order_id_from_url(driver.current_url)
    return Transaction(id=id, shipped_date=shipped_date, price=price, order_id=order_id)


def get_book_item(driver) -> Item:
    try:
        elem = driver.find_element_by_xpath(
            "//a[contains(@href, 'https://www.amazon.ca/dp/')]"
        )
    except NoSuchElementException:
        return None
    url = elem.get_attribute("href")
    name = elem.text
    price_elem = elem.find_element_by_xpath("./../../../td[contains(text(), 'CDN')]")
    price = price_elem.text.replace("CDN$ ", "")
    elem = driver.find_element_by_xpath("//*[contains(text(), 'Digital Order:')]")
    shipped_date_text = elem.text.split("Digital Order: ")[1]
    shipped_date = normalize_datestr(shipped_date_text)
    print(f"{shipped_date} - {price} - {url[20:50]} - {name[:20]}")

    id = gen_primary_key(f"{name}{url}{shipped_date}{price}")
    order_id = get_order_id_from_url(driver.current_url)
    return Item(
        id=id,
        name=name,
        url=url,
        shipped_date=shipped_date,
        price=float(price),
        quantity=1,
        order_id=order_id,
    )


def get_amazon_order(driver) -> Order:
    ordered_date_elem = driver.find_element_by_xpath(
        "//span[contains(text(), 'Ordered on ')]"
    )
    ordered_date_text = ordered_date_elem.text.replace("Ordered on ", "")
    ordered_date = normalize_datestr(ordered_date_text)

    order_subtotals = driver.find_element_by_id(
        "od-subtotals"
    ).find_elements_by_class_name("a-row")
    tax = 0
    for subtotal in order_subtotals:
        try:
            subtotal_name = subtotal.find_elements_by_class_name("a-column")[0].text
            subtotal_price = subtotal.find_elements_by_class_name("a-column")[1].text
            if subtotal_name == "Grand Total:":
                grand_total = float(subtotal_price.replace("CDN$", ""))
            if subtotal_name == "Total before tax:":
                total_before_tax = float(subtotal_price.replace("CDN$", ""))
            if subtotal_name in ("Estimated GST/HST:", "Estimated PST/RST/QST:"):
                tax += float(subtotal_price.replace("CDN$", ""))

        except IndexError:
            # This ignores the seperator elements
            continue

    order_id = get_order_id_from_url(driver.current_url)

    print(order_id, ordered_date, grand_total, total_before_tax, tax)

    return Order(
        id=order_id,
        url=driver.current_url,
        ordered_date=ordered_date,
        grand_total=grand_total,
        total_before_tax=total_before_tax,
        tax=tax,
    )


def get_amazon_transactions(driver) -> List[Transaction]:
    """Gets transactions from order detail page. May return more than one."""
    transactions = []

    try:
        elem = driver.find_element_by_xpath("//span[contains(text(), 'Transactions')]")
        elem.click()
    except NoSuchElementException:
        print("No transaction here, skip")
        return []

    # Get transactions infos
    elems = driver.find_elements_by_xpath(
        "//span[contains(text(), 'Visa ending in 5173')]"
    )
    for transaction in elems:
        shipped_date_text = transaction.text.split(" - ")[0]
        shipped_date = normalize_datestr(shipped_date_text)

        price = transaction.text.split("CDN$ ")[1]
        id = gen_primary_key(f"{shipped_date}{price}")
        order_id = get_order_id_from_url(driver.current_url)
        transactions.append(
            Transaction(
                id=id, shipped_date=shipped_date, price=price, order_id=order_id
            )
        )

    return transactions


def get_amazon_items(driver) -> List[Item]:
    items = []
    order_id = get_order_id_from_url(driver.current_url)

    # Get all the items information
    elems = driver.find_elements_by_class_name("shipment-is-delivered")
    for shipment_box in elems:
        # I need a way to get the individual item info
        try:
            shipped_date_text = (
                shipment_box.find_element_by_class_name("js-shipment-info-container")
                .find_element_by_xpath(".//span[contains(text(), 'Delivered')]")
                .text.split("Delivered ")[1]
            )
            shipped_date = normalize_datestr(shipped_date_text)
        except NoSuchElementException:
            shipped_date = "Not delivered (return, redelivery, etc...)"

        item_sold_bys = shipment_box.find_elements_by_xpath(
            ".//span[contains(text(), 'Sold by:')]"
        )

        # expand to all items
        for item_box in item_sold_bys:
            item_box_info = item_box.find_element_by_xpath("../..")

            name = item_box_info.find_element_by_class_name("a-link-normal").text
            url = item_box_info.find_element_by_class_name(
                "a-link-normal"
            ).get_attribute("href")
            price = item_box_info.find_element_by_class_name(
                "a-color-price"
            ).text.split(" ")[1]
            try:
                quantity = (
                    item_box_info.find_element_by_xpath("..")
                    .find_element_by_class_name("item-view-qty")
                    .text
                )
            except:
                quantity = 1

            print(f"{shipped_date} - {price} - {url[20:50]} - {name[:20]} - {quantity}")

            id = gen_primary_key(f"{name}{url}{shipped_date}{price}")
            items.append(
                Item(
                    id=id,
                    name=name,
                    url=url,
                    shipped_date=shipped_date,
                    price=float(price),
                    quantity=int(quantity),
                    order_id=order_id,
                )
            )

    return items


@click.command("scrape-amazon-orders")
@with_appcontext
def main():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://www.amazon.ca/gp/your-account/order-history")

    amazon_sign_in(driver)

    order_urls = get_order_urls(driver)

    orders_info = []
    transactions_info = []
    items_info = []

    for order_url in order_urls:
        driver.get(order_url)
        time.sleep(1)

        try:
            amazon_sign_in(driver)
        except NoSuchElementException:
            print("already signed in")

        if "/gp/digital/your-account/" in order_url:
            book_transaction = get_book_transaction(driver)
            orders_info.append(
                Order(
                    id=book_transaction.order_id,
                    url=order_url,
                    ordered_date=book_transaction.shipped_date,
                    grand_total=book_transaction.price,
                )
            )
            transactions_info.append(book_transaction)
            book = get_book_item(driver)
            if book:
                items_info.append(book)
        else:
            orders_info.append(get_amazon_order(driver))
            transactions_info.extend(get_amazon_transactions(driver))
            items_info.extend(get_amazon_items(driver))

    orders_df = pd.DataFrame([order.__dict__ for order in orders_info])
    trans_df = pd.DataFrame(
        [transaction.__dict__ for transaction in transactions_info]
    )
    items_df = pd.DataFrame([item.__dict__ for item in items_info])

    # get items -> transactions linked
    items_df["pre_tax"] = (
        items_df.assign(price=items_df.price * items_df.quantity)
        .groupby(["shipped_date", "order_id"])
        .transform("sum")["price"]
    )
    items_df["min_price"] = items_df["pre_tax"].apply(lambda x: round(x * 1))
    items_df["max_price"] = items_df["pre_tax"].apply(lambda x: round(x * CDN_TAX, 1))

    items_df["shipped_date_clean"] = items_df["shipped_date"].apply(
        lambda x: "2000-01-01" if "Not delivered" in x else x
    )
    items_df["min_shipped_date"] = pd.DatetimeIndex(
        items_df["shipped_date_clean"]
    ) - pd.DateOffset(1)
    items_df["max_shipped_date"] = pd.DatetimeIndex(
        items_df["shipped_date_clean"]
    ) + pd.DateOffset(1)

    trans_df["transaction_price"] = trans_df["price"].apply(
        lambda x: round(float(x), 1)
    )
    trans_df["shipped_date_datetime"] = pd.DatetimeIndex(
        trans_df["shipped_date"]
    )

    # Join logic is:
    #   a. transaction price is between min-max range for the sum of items (min is all no tax, max is all CDN_TAX)
    #   b. shipped_date between transaction and items is within +/- 1 days
    item_columns = [
        "id",
        "name",
        "url",
        "shipped_date",
        "price",
        "quantity",
        "transaction_id",
        "order_id",
    ]

    # remove items that have 0 price.
    items_df = items_df.query("price != 0.00")
    trans_df = trans_df.query("transaction_price != 0.00")

    # To ensure one-to-one joins only we do:
    # 1. rows that are the only item in an order HAVE to match the transaction of that order
    one_to_one_match_rows = (
        items_df.copy()
        .merge(trans_df, on="order_id", how="left")
        .set_index(["id_x", "id_y"])
        .groupby("order_id")
        .transform("count")
        .query("name == 1")
        .reset_index()
        .loc[:, ["id_x", "id_y"]]
        .merge(
            items_df, left_on="id_x", right_on="id", how="inner", suffixes=["_x", ""]
        )
        .drop(columns=["id", "transaction_id"])
        .rename(columns={"id_x": "id", "id_y": "transaction_id"})
        .loc[:, item_columns]
    )
    items_df = items_df[~items_df.id.isin(one_to_one_match_rows.id)]
    trans_df = trans_df[~trans_df.id.isin(one_to_one_match_rows.transaction_id)]


    # 2. rows that are an exact match to transaction price and in shipped_date range
    exact_match_to_price = (
        items_df.copy()
        .merge(
            trans_df,
            left_on=["order_id", "max_price"],
            right_on=["order_id", "transaction_price"],
            how="left",
        )
        .query("min_shipped_date <= shipped_date_datetime <= max_shipped_date")
        .loc[:, ["id_x", "id_y"]]
        .merge(items_df, left_on="id_x", right_on="id", how="right")
        .dropna(subset=["id_x"])
        .drop(columns=["transaction_id"])
        .rename(columns={"id_y": "transaction_id"})
        .loc[:, item_columns]
    )

    items_df = items_df[~items_df.id.isin(exact_match_to_price.id)]
    trans_df = trans_df[~trans_df.id.isin(exact_match_to_price.transaction_id)]

    # 3. rows that are in price range and shipped_date range
    match_to_both = (
        items_df.copy()
        .merge(trans_df, on="order_id", how="inner")
        .query("min_price <= transaction_price <= max_price")
        .query("min_shipped_date <= shipped_date_datetime <= max_shipped_date")
        .loc[:, ["id_x", "id_y"]]
        .merge(items_df, left_on="id_x", right_on="id", how="right")
        .dropna(subset=["id_x"])
        .drop(columns=["transaction_id"])
        .rename(columns={"id_y": "transaction_id"})
        .loc[:, item_columns]
    )

    items_df = items_df[~items_df.id.isin(match_to_both.id)]
    trans_df = trans_df[~trans_df.id.isin(match_to_both.transaction_id)]


    # 4. rows that are just in price range
    match_to_price_range = (
        items_df.copy()
        .merge(trans_df, on="order_id", how="inner")
        .query("min_price <= transaction_price <= max_price")
        .loc[:, ["id_x", "id_y"]]
        .merge(items_df, left_on="id_x", right_on="id", how="right")
        .dropna(subset=["id_x"])
        .drop(columns=["transaction_id"])
        .rename(columns={"id_y": "transaction_id"})
        .loc[:, item_columns]
    )
    items_df = items_df[~items_df.id.isin(match_to_price_range.id)]
    trans_df = trans_df[~trans_df.id.isin(match_to_price_range.transaction_id)]


    # 5. Allow for rounding errors in price match
    match_to_price_range_no_decimal = (
        items_df.copy()
        .merge(trans_df, on="order_id", how="inner")
        .query("min_price*0.99 <= transaction_price <= max_price*1.01")
        .loc[:, ["id_x", "id_y"]]
        .merge(items_df, left_on="id_x", right_on="id", how="right")
        .dropna(subset=["id_x"])
        .drop(columns=["transaction_id"])
        .rename(columns={"id_y": "transaction_id"})
        .loc[:, item_columns]
    )
    items_df = items_df[~items_df.id.isin(match_to_price_range_no_decimal.id)]
    trans_df = trans_df[~trans_df.id.isin(match_to_price_range_no_decimal.transaction_id)]


    # 6. Ignore the groupby shipping date for remaining transactions
    items_df["taxed_price"] = items_df["price"].apply(lambda x: round(x * CDN_TAX, 1))
    ignore_groupped_price = (
        items_df.copy()
        .merge(trans_df, on="order_id", how="inner")
        .query("taxed_price == transaction_price")
        .loc[:, ["id_x", "id_y"]]
        .merge(
            items_df, left_on="id_x", right_on="id", how="inner", suffixes=["_x", ""]
        )
        .drop(columns=["id", "transaction_id"])
        .rename(columns={"id_x": "id", "id_y": "transaction_id"})
        .loc[:, item_columns]
    )
    items_df = items_df[~items_df.id.isin(ignore_groupped_price.id)]
    trans_df = trans_df[~trans_df.id.isin(ignore_groupped_price.transaction_id)]

    # TODO
    # 7. If there is one remaining, match it to transaction; otherwise leave them unknown
    # only_one_remaining = ()

    full_items_df = pd.concat(
        [
            one_to_one_match_rows,
            exact_match_to_price,
            match_to_both,
            match_to_price_range,
            match_to_price_range_no_decimal,
            ignore_groupped_price,
            # only_one_remaining,
        ]
    )
    full_items_df["category"] = pd.Series()

    # Write the dataframes to the postgres database
    write_df_to_database(orders_df, "amazon_orders")
    write_df_to_database(
        trans_df[["id", "shipped_date", "price", "order_id"]],
        "amazon_transactions",
    )
    write_df_to_database(full_items_df, "amazon_items")

    driver.close()


if __name__ == "__main__":
    main()
