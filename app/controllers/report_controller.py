from fastapi import APIRouter, Depends
from sqlalchemy.engine import Connection

from app.db import get_warehouse_connection
from app.repositories import report_repository

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/top-sales")
def top_sales(conn: Connection = Depends(get_warehouse_connection)):
    return report_repository.top_sales(conn)