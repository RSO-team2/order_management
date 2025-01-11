from datetime import datetime
from typing import List

import psycopg2
from dotenv import load_dotenv

load_dotenv()

import os


def make_connection():
    """
    Establishes a connection to the PostgreSQL database using the connection URL
    provided in the environment variable 'DATABASE_URL'.

    Returns:
        tuple: A tuple containing the connection object and the cursor object.
    """
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    return conn, cursor


def get_current_date():
    """
    Returns the current date and time as a formatted string.

    The date and time are formatted as "DD/MM/YYYY HH:MM:SS".

    Returns:
        str: The current date and time in the format "DD/MM/YYYY HH:MM:SS".
    """
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def insert_order(cursor, data):
    """
    Inserts a new order into the orders table and returns the generated order ID.

    Args:
        cursor (psycopg2.cursor): The database cursor to execute the SQL command.
        data (dict): A dictionary containing the order details with the following keys:
            - customer_id (int): The ID of the customer placing the order.
            - order_date (str): The date and time when the order was placed.
            - total_amount (float): The total amount for the order.
            - items (str): A JSON string representing the items in the order.
            - restaurant_id (int): The ID of the restaurant fulfilling the order.
            - status (str): The current status of the order.
            - delivery_address (str): The delivery address for the order.

    Returns:
        int: The ID of the newly inserted order.
    """
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
    """
    Retrieve all orders for a specific customer from the database.

    Args:
        cursor (object): Database cursor object used to execute SQL queries.
        customer_id (int): The ID of the customer whose orders are to be retrieved.

    Returns:
        list: A list of orders associated with the specified customer.
    """
    cursor.execute(
        """
        SELECT * FROM orders WHERE customer_id = %s;
        """,
        (customer_id,),
    )
    orders = cursor.fetchall()
    return orders


def commit_and_close(conn, cursor):
    """
    Commits the current transaction, closes the cursor, and closes the connection.

    Args:
        conn (sqlite3.Connection): The database connection object.
        cursor (sqlite3.Cursor): The database cursor object.
    """
    conn.commit()
    cursor.close()
    conn.close()


def check_database_connection():
    try:
        # Connect to your PostgreSQL database
        connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = connection.cursor()
        cursor.execute(
            "SELECT 1"
        )  # Simple query to check if the database is responsive
        connection.close()
        print("Database is connected!")
    except OperationalError as err:
        raise Exception("Database is not reachable: " + str(err))
