from sqlalchemy import create_engine
from app.config import settings

source_engine = create_engine(settings.source_db_url, pool_pre_ping=True)
warehouse_engine = create_engine(settings.warehouse_db_url, pool_size=5, pool_pre_ping=True)