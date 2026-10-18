"""Route for the Overview page: GET /api/overview."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.engine import Connection
from sqlalchemy.exc import NoSuchTableError, OperationalError, ProgrammingError

from app.db import get_warehouse_connection
from app.repositories import overview_repository

router = APIRouter(prefix="/overview", tags=["overview"])


@router.get("")
def overview(conn: Connection = Depends(get_warehouse_connection)):
    try:
        return [overview_repository.summary(conn)]
    except (NoSuchTableError, ProgrammingError):
        raise HTTPException(status_code=404, detail="Warehouse tables aren't loaded yet. Create them and run the ETL first.")
    except OperationalError:
        raise HTTPException(status_code=503, detail="Can't reach the warehouse database. Is the MySQL container running?")
