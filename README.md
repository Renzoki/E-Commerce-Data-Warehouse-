## Project Directory

```text
app/
├── controllers/          # FastAPI routers per report group (URL & query parameter declaration)
├── repositories/         # ALL SQL queries 
├── schemas/              # DTO for request/response shapes
├── services/             # Business logic
data/                     # Source database dumps & raw SQL files 
docker/
└── mysql/
    └── conf/
        └── my.cnf        # MySQL container configuration 
    └── init/             # Database init
etl/
├── extract.py            # Source database chunked reads returning DataFrames
├── transform.py          # Pure functions for data cleaning, reshaping, and dimension generation
├── load.py               # Batch inserts into the warehouse dimension and fact tables
├── run_etl.py            # Pipeline orchestrator executing extract -> transform -> load
└── validate.py           # Post-ETL verification script (row counts and warehouse vs source totals)
sql/                      # Warehouse setup scripts
tests/