"""Routes for the Browse page: GET /api/tables and GET /api/tables/{name}."""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.engine import Connection
from sqlalchemy.exc import OperationalError

from app.db import get_warehouse_connection
from app.services import table_service

router = APIRouter(prefix="/tables", tags=["tables"])


@router.get("")
def list_tables():
    return table_service.list_tables()


@router.get("/{name}")
def browse_table(
    name: str,
    q: str = "",
    sort: str | None = None,
    order: Literal["asc", "desc"] = "asc",
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    conn: Connection = Depends(get_warehouse_connection),
):
    try:
        return table_service.browse(conn, name, q, sort, order, limit, offset)
    except table_service.TableNotAllowed as e:
        raise HTTPException(status_code=404, detail=str(e))
    except table_service.TableMissing as e:
        raise HTTPException(status_code=404, detail=str(e))
    except table_service.BadColumn as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OperationalError:
        raise HTTPException(status_code=503, detail="Can't reach the warehouse database. Is the MySQL container running?")
