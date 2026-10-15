import pandas as pd
from sqlalchemy import text

from app.db import source_engine
from etl.extract import count_rows

TABLES = ["Couriers", "Riders", "Users", "Products", "Orders", "OrderItems"]

def query(sql):
    with source_engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


def show(title, sql):
    print(f"\n{title}")
    print(query(sql).to_string(index=False))


def formats(table, column):
    # digits become 9 and letters become a, so each distinct format appears once
    return f"""
        SELECT REGEXP_REPLACE(REGEXP_REPLACE({column}, '[0-9]', '9'), '[A-Za-z]', 'a') AS pattern,
               COUNT(*) AS n, MIN({column}) AS example
        FROM {table} GROUP BY pattern ORDER BY n DESC LIMIT 10
    """


def values(table, column):
    # case-sensitive
    return f"""
        SELECT {column} COLLATE utf8mb4_bin AS value, COUNT(*) AS n
        FROM {table} GROUP BY value ORDER BY LOWER(value)
    """


def slash_order(table, column):
    # if the first part is ever above 12 it is the day (DD/MM), if the second is, it is MM/DD
    return f"""
        SELECT SUM(CAST(SUBSTRING_INDEX({column}, '/', 1) AS UNSIGNED) > 12) AS first_part_over_12,
               SUM(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX({column}, '/', 2), '/', -1) AS UNSIGNED) > 12) AS second_part_over_12
        FROM {table} WHERE {column} LIKE '%/%'
    """


if __name__ == "__main__":
    print("Row counts")
    for t in TABLES:
        print(f"  {t}: {count_rows(t)}")

    print("\nColumns with NULLs")
    for t in TABLES:
        cols = query(f"SELECT * FROM {t} LIMIT 0").columns
        sums = ", ".join("SUM(%s IS NULL) AS %s" % (c, c) for c in cols)
        for col, n in query(f"SELECT {sums} FROM {t}").iloc[0].items():
            if n > 0:
                print(f"  {t}.{col}: {int(n)}")

    show("Orders.deliveryDate formats", formats("Orders", "deliveryDate"))
    show("Users.dateOfBirth formats", formats("Users", "dateOfBirth"))
    show("Users.zipCode formats", formats("Users", "zipCode"))

    show("Orders.deliveryDate slash dates", slash_order("Orders", "deliveryDate"))
    show("Users.dateOfBirth slash dates", slash_order("Users", "dateOfBirth"))

    show("Users.gender", values("Users", "gender"))
    show("Riders.gender", values("Riders", "gender"))
    show("Riders.vehicleType", values("Riders", "vehicleType"))
    show("Products.category", values("Products", "category"))

    show("Orders.createdAt range", "SELECT MIN(createdAt) AS first, MAX(createdAt) AS last FROM Orders")