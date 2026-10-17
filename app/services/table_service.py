"""Validation for the Browse page's table reads."""
from sqlalchemy.engine import Connection
from sqlalchemy.exc import NoSuchTableError

from app.repositories import table_repository

# Only these tables can be browsed. Matches the ecommerce_dw star schema.
WAREHOUSE_TABLES = ("fact_sales", "dim_date", "dim_customer", "dim_product", "dim_rider")


class TableNotAllowed(ValueError):
    pass


class TableMissing(LookupError):
    pass


class BadColumn(ValueError):
    pass


def list_tables() -> list[str]:
    return list(WAREHOUSE_TABLES)


def browse(
    conn: Connection,
    name: str,
    q: str = "",
    sort: str | None = None,
    order: str = "asc",
    limit: int = 50,
    offset: int = 0,
) -> dict:
    if name not in WAREHOUSE_TABLES:
        raise TableNotAllowed(f"'{name}' is not a warehouse table. Allowed: {', '.join(WAREHOUSE_TABLES)}")

    try:
        columns = table_repository.column_names(conn, name)
    except NoSuchTableError:
        table_repository.forget_table(name)
        raise TableMissing(f"Table '{name}' doesn't exist in the warehouse yet. Create it and run the ETL first.")

    if sort and sort not in columns:
        raise BadColumn(f"Can't sort by '{sort}': {name} has no such column.")

    rows, total = table_repository.fetch_rows(conn, name, q.strip(), sort, order, limit, offset)
    return {"rows": rows, "total": total, "columns": columns}
