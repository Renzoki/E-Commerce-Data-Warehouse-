"""Generic read access to warehouse tables for the Browse page.

Not an OLAP query: it only pages through a table's rows. Built with
SQLAlchemy Core (no SQL strings), so table/column names never come from
user input and search terms are bound parameters.
"""
from sqlalchemy import MetaData, String, Table, cast, func, or_, select
from sqlalchemy.engine import Connection

_metadata = MetaData()


def get_table(conn: Connection, name: str) -> Table:
    """Reflect a table from ecommerce_dw (cached after first use)."""
    if name in _metadata.tables:
        return _metadata.tables[name]
    return Table(name, _metadata, autoload_with=conn)


def forget_table(name: str) -> None:
    """Drop a cached table definition (e.g. after it was missing or rebuilt)."""
    if name in _metadata.tables:
        _metadata.remove(_metadata.tables[name])


def column_names(conn: Connection, name: str) -> list[str]:
    return [c.name for c in get_table(conn, name).columns]


def fetch_rows(
    conn: Connection,
    name: str,
    q: str,
    sort: str | None,
    order: str,
    limit: int,
    offset: int,
) -> tuple[list[dict], int]:
    """One page of rows plus the total row count after the search filter."""
    table = get_table(conn, name)
    rows_stmt = select(table)
    count_stmt = select(func.count()).select_from(table)

    if q:
        # match the text in any column; autoescape treats % and _ literally
        match = or_(*(cast(col, String).contains(q, autoescape=True) for col in table.columns))
        rows_stmt = rows_stmt.where(match)
        count_stmt = count_stmt.where(match)

    if sort:
        col = table.c[sort]
        rows_stmt = rows_stmt.order_by(col.desc() if order == "desc" else col.asc())

    rows_stmt = rows_stmt.limit(limit).offset(offset)

    rows = [dict(r._mapping) for r in conn.execute(rows_stmt)]
    total = conn.execute(count_stmt).scalar_one()
    return rows, total
