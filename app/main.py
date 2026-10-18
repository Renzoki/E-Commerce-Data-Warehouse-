from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.controllers import table_controller

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="E-Commerce OLAP")

@app.get("/health")
def health():
    return {"status": "ok"}

# API routers — prefix them with /api so they never clash with pages.
app.include_router(table_controller.router, prefix="/api")
# app.include_router(report_controller.router, prefix="/api")

# Keep this LAST: it serves frontend/ at "/" and would shadow any route added after it.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
