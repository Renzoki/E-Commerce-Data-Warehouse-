from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.controllers import table_controller
from app.controllers import report_controller
from app.controllers import overview_controller

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="E-Commerce OLAP")

# Make the browser re-check frontend files on every load, so edits to the
# HTML/JS/CSS show up on a normal refresh instead of a stale cached copy.
@app.middleware("http")
async def no_cache_frontend(request, call_next):
    response = await call_next(request)
    if not request.url.path.startswith("/api"):
        response.headers["Cache-Control"] = "no-cache"
    return response


@app.get("/health")
def health():
    return {"status": "ok"}

# API routers — prefix them with /api so they never clash with pages.
app.include_router(table_controller.router, prefix="/api")
app.include_router(report_controller.router, prefix="/api")
app.include_router(overview_controller.router, prefix="/api")

# Keep this LAST: it serves frontend/ at "/" and would shadow any route added after it.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
