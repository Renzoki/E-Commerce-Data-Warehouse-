from fastapi import APIRouter, Depends
from sqlalchemy.engine import Connection
from typing import Literal
from app.db import get_warehouse_connection
from app.repositories import report_repository

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/top-sales")
def top_sales(conn: Connection = Depends(get_warehouse_connection)):
    return report_repository.top_sales(conn)

@router.get("/sales-by-location")
def sales_by_location(
    level: Literal["city", "country"] = "city",
    conn: Connection = Depends(get_warehouse_connection)
):
    return report_repository.sales_by_location(conn, level)
