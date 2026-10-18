# Frontend

Vanilla HTML/CSS/JS. No build step. Chart.js loads from a CDN on the Reports page.

## Run

```powershell
uv run uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 — FastAPI serves this folder at `/`, so the pages and API share one origin (no CORS needed).

## Pages

| Page | File | Driven by |
|---|---|---|
| Overview | `index.html` | `CONFIG.overview` + `CONFIG.kpis` |
| Browse | `browse.html` | `CONFIG.datasets` |
| Reports | `reports.html` | `CONFIG.reports` |
| Schema | `schema.html` | `CONFIG.schema` (the star schema) |

## What's live vs mock

- **Browse is connected to `ecommerce_dw`.** `GET /api/tables/{name}` pages through the five star-schema tables (search, sort, paging done in the database). Code: `app/controllers/table_controller.py` → `app/services/table_service.py` → `app/repositories/table_repository.py`. This only reads rows; it is not an OLAP query.
- **Overview is connected.** `GET /api/overview` returns one row of whole-warehouse totals (revenue, orders, units, customers, products, riders, couriers, first/last delivery date). Code: `app/controllers/overview_controller.py` → `app/repositories/overview_repository.py`. Plain counts/sums, not an OLAP report.
- **Reports** are connected through `app/controllers/report_controller.py`; any report whose `endpoint` is `""` falls back to mock.
- A table that isn't created yet shows a "doesn't exist in the warehouse yet" message instead of crashing.

## Hooking up a query

Everything is configured in `js/config.js`. To connect one item:

1. Write the endpoint in FastAPI (under `/api/...`).
2. Put its path in that item's `endpoint` field.
3. Set `USE_MOCK: false`.

Items whose `endpoint` is still `""` keep showing mock data from `js/mock.js`, so you can connect them one at a time.

### Response shapes

- **Report / client-side dataset:** a JSON array of row objects.
  `[{"period": "2024", "revenue": 1234.5}, ...]`
- **Overview:** one row with every KPI field, `[{"total_revenue": 123.4, "total_orders": 10, ...}]`; each tile in `CONFIG.kpis` names its `field`.
- **Server-side dataset (`server: true`):** receives `q, sort, order, limit, offset` as query params and returns `{"rows": [...], "total": 12345}`. Use this for large fact tables.

Report `params` are sent as query params with the same `name`, e.g. `?level=quarter` for roll-up / drill-down.

Column names in the table come straight from the JSON keys, so alias them in SQL (`AS revenue`) to get readable headers.

## Files

```text
frontend/
├── index.html / browse.html / reports.html / schema.html
├── css/style.css
└── js/
    ├── config.js     # endpoints + page setup (edit this)
    ├── mock.js       # placeholder data, delete as endpoints go live
    ├── api.js        # fetch + table rendering helpers
    ├── layout.js     # shared nav/footer, /health status
    ├── overview.js / browse.js / reports.js / schema.js
```
