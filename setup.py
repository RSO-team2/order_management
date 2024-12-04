import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

print("Creating database tables...")

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS orders;") #TODO: Remove later when all of the databases are setup
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        customer_id INT,
        order_date DATE,
        total_amount DECIMAL(10, 2),
        items TEXT[],
        restaurant_id INT,
        status INT
    );
"""
)

cursor.execute(
    "select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"
)
print("The databse cluster contains the following tables:")
print(cursor.fetchall())

conn.commit()
cursor.close()
conn.close()
