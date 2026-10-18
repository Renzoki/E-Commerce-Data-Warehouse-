"""
    uv run python -m etl.run_etl
"""
import time
from pathlib import Path

import pandas as pd

from etl import transform as t
from etl.extract import count_rows, extract_all, extract_table
from etl.load import clear_warehouse, count_warehouse_rows, load_dataframe

REJECTED_LOG = Path(__file__).resolve().parent.parent / "logs" / "rejected_fact_rows.csv"


def load_timed(table: str, df: pd.DataFrame) -> int:
    start = time.perf_counter()
    load_dataframe(df, table)
    print(f"{table}: {len(df)} rows ({time.perf_counter() - start:.1f}s)")
    return len(df)


def run() -> dict:
    began = time.perf_counter()
    REJECTED_LOG.parent.mkdir(exist_ok=True)
    REJECTED_LOG.unlink(missing_ok=True)

    clear_warehouse()
    print("warehouse cleared")

    # dimensions built from the small and medium tables
    dim_customer = t.build_dim_customer(extract_all("Users"))
    dim_product = t.build_dim_product(extract_all("Products"))
    dim_rider = t.build_dim_rider(extract_all("Riders"), extract_all("Couriers"))

    # one row per order with its dimension keys looked up (1,000,000 rows kept in memory)
    orders = pd.concat([t.prepare_orders(chunk, dim_customer, dim_rider)
                        for chunk in extract_table("Orders")])

    # the date dimension covers every day between the first and last delivery date
    keys = orders["date_key"].dropna().astype("int64").astype(str)
    dim_date = t.build_dim_date(pd.to_datetime(keys, format="%Y%m%d"))

    counts = {
        "dim_date": load_timed("dim_date", dim_date),
        "dim_customer": load_timed("dim_customer", dim_customer),
        "dim_product": load_timed("dim_product", dim_product),
        "dim_rider": load_timed("dim_rider", dim_rider),
    }

    # fact table: order items in chunks, so memory stays flat
    start = time.perf_counter()
    fact_rows = rejected_rows = 0
    for chunk in extract_table("OrderItems"):
        fact, rejected = t.build_fact_sales(chunk, orders, dim_product)
        load_dataframe(fact, "fact_sales")
        fact_rows += len(fact)
        if len(rejected):
            rejected.to_csv(REJECTED_LOG, mode="a", header=not REJECTED_LOG.exists(), index=False)
            rejected_rows += len(rejected)
    counts["fact_sales"] = fact_rows
    print(f"fact_sales: {fact_rows} rows ({time.perf_counter() - start:.1f}s), rejected: {rejected_rows}")

    # every source row must be either loaded or rejected
    source_items = count_rows("OrderItems")
    if fact_rows + rejected_rows != source_items:
        raise RuntimeError(f"OrderItems rows do not add up: {fact_rows} loaded + "
                           f"{rejected_rows} rejected != {source_items} in source")

    # confirm the database itself holds what we loaded
    for table, expected in counts.items():
        actual = count_warehouse_rows(table)
        if actual != expected:
            raise RuntimeError(f"{table}: loaded {expected} rows but the warehouse has {actual}")

    seconds = round(time.perf_counter() - began, 1)
    print(f"done in {seconds}s")
    return {"loaded": counts, "rejected": rejected_rows, "seconds": seconds}


if __name__ == "__main__":
    run()