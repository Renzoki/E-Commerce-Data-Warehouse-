"""Headline totals for the Overview page.

Not an OLAP report: just whole-warehouse counts and sums (no grouping,
no roll-up). Built with SQLAlchemy Core like table_repository.
"""
from sqlalchemy import Table, distinct, func, select
from sqlalchemy.engine import Connection

from app.repositories.table_repository import get_table


def _count(conn: Connection, table: Table) -> int:
    return conn.execute(select(func.count()).select_from(table)).scalar_one()


def summary(conn: Connection) -> dict:
    fact = get_table(conn, "fact_sales")
    date = get_table(conn, "dim_date")
    rider = get_table(conn, "dim_rider")

    sales = conn.execute(
        select(
            func.coalesce(func.sum(fact.c.line_amount), 0).label("total_revenue"),
            func.count(distinct(fact.c.order_id)).label("total_orders"),
            func.count().label("order_lines"),
            func.coalesce(func.sum(fact.c.quantity), 0).label("units_sold"),
        )
    ).one()._mapping

    period = conn.execute(
        select(
            func.min(date.c.full_date).label("first_date"),
            func.max(date.c.full_date).label("last_date"),
        ).select_from(fact.join(date, fact.c.date_key == date.c.date_key))
    ).one()._mapping

    orders = sales["total_orders"]
    return {
        "total_revenue": float(sales["total_revenue"]),
        "total_orders": orders,
        "order_lines": sales["order_lines"],
        "units_sold": int(sales["units_sold"]),
        "avg_order_value": float(sales["total_revenue"]) / orders if orders else 0,
        "customers": _count(conn, get_table(conn, "dim_customer")),
        "products": _count(conn, get_table(conn, "dim_product")),
        "riders": _count(conn, rider),
        "couriers": conn.execute(select(func.count(distinct(rider.c.courier_name)))).scalar_one(),
        "first_date": period["first_date"].isoformat() if period["first_date"] else None,
        "last_date": period["last_date"].isoformat() if period["last_date"] else None,
    }
