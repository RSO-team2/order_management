from datetime import datetime
from typing import List

import psycopg2
from dotenv import load_dotenv

load_dotenv()

import os


def make_connection():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    return conn, cursor


def vaildate_order_data(data):
    if not data:
        return {"result": False, "error": "no data provided"}
    if not data.get("restaurant_id") or not isinstance(data.get("restaurant_id"), int):
        return {"result": False, "error": "invalid restaurant id"}
    if (
        not data.get("items")
        or not isinstance(data.get("items"), List)
        or not all(isinstance(x, int) for x in data.get("items"))
    ):
        return {"result": False, "error": "order items invalid"}
    if not data.get("customer_id") or not isinstance(data.get("customer_id"), int):
        return {"result": False, "error": "invalid customer id"}
    if not data.get("total_amount") or not isinstance(data.get("total_amount"), float):
        return {"result": False, "error": "invalid total price"}
    if not data.get("delivery_address") or not isinstance(
        data.get("delivery_address"), str
    ):
        return {
            "result": False,
            "error": "invalid delivery address",
        }  # TODO: Read address from user database here
    return {"result": True}


def get_current_date():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def insert_order(cursor, data):
    cursor.execute(
        """
        INSERT INTO orders (customer_id, order_date, total_amount, items, restaurant_id, status, delivery_address)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (
            data["customer_id"],
            data["order_date"],
            data["total_amount"],
            data["items"],
            data["restaurant_id"],
            data["status"],
            data["delivery_address"],
        ),
    )
    order_id = cursor.fetchone()[0]
    return order_id


def get_user_orders(cursor, customer_id):
    cursor.execute(
        """
        SELECT * FROM orders WHERE customer_id = %s;
        """,
        (customer_id,),
    )
    orders = cursor.fetchall()
    return orders


def commit_and_close(conn, cursor):
    conn.commit()
    cursor.close()
    conn.close()
