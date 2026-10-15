from collections.abc import Iterator

import pandas as pd
from sqlalchemy import text

from app.db import source_engine

SOURCE_TABLES = {"Couriers", "Riders", "Users", "Products", "Orders", "OrderItems"}

# check if tables match the given
def _check(table: str) -> None:
    if table not in SOURCE_TABLES:
        raise ValueError(f"Unknown source table: {table}")

def count_rows(table: str) -> int:
    _check(table)
    with source_engine.connect() as conn:
        return conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar()

# for bigger tables, extract chunk by chunk
def extract_table(table: str, chunk_size: int = 50_000) -> Iterator[pd.DataFrame]:
    _check(table)
    with source_engine.connect().execution_options(stream_results=True) as conn:
        yield from pd.read_sql(text(f"SELECT * FROM `{table}`"), conn, chunksize=chunk_size)

# for smaller tables that can be extracted fully at once
def extract_all(table: str) -> pd.DataFrame:
    frames = list(extract_table(table))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()