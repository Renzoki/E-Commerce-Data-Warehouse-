"""Writes DataFrames into ecommerce_dw."""
import pandas as pd
from sqlalchemy import text

from app.db import warehouse_engine

# dimensions first
LOAD_ORDER = ["dim_date", "dim_customer", "dim_product", "dim_rider", "fact_sales"]

def clear_warehouse() -> None:
    """Empty every table, fact first. Foreign key checks are off only while truncating."""
    with warehouse_engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        try:
            for table in reversed(LOAD_ORDER):
                conn.execute(text(f"TRUNCATE TABLE `{table}`"))
        finally:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            conn.commit()


def load_dataframe(df: pd.DataFrame, table: str, chunk_size: int = 10_000) -> int:
    if table not in LOAD_ORDER:
        raise ValueError(f"Unknown warehouse table: {table}")
    df.to_sql(table, warehouse_engine, if_exists="append", index=False, chunksize=chunk_size)
    return len(df)


def count_warehouse_rows(table: str) -> int:
    if table not in LOAD_ORDER:
        raise ValueError(f"Unknown warehouse table: {table}")
    with warehouse_engine.connect() as conn:
        return conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar()