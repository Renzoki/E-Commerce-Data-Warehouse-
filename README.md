## Project Directory

```text
app/
├── controllers/          # FastAPI routers per report group (URL & query parameter declaration)
├── repositories/         # ALL SQL queries
├── schemas/              # DTOs for request/response shapes
├── services/             # Business logic (validation, roll-up/drill-down level selection)
├── config.py             # Settings loaded from .env
├── db.py                 # Engines: source (read-only) and warehouse
├── exceptions.py         # Custom errors and exception handlers
└── main.py               # FastAPI app entry point
data/                     # Source database dumps (git-ignored, shared separately)
docker/
└── mysql/
    ├── conf/
    │   └── my.cnf        # MySQL container configuration
    └── init/
        └── 01_init.sh    # First-boot init: creates ecommerce_source, grants read-only access
etl/
├── extract.py            # Source database chunked reads returning DataFrames
├── transform.py          # Pure functions for data cleaning, reshaping, and dimension generation
├── load.py               # Batch inserts into the warehouse dimension and fact tables
├── run_etl.py            # Pipeline orchestrator executing extract -> transform -> load
└── validate.py           # Post-ETL verification (row counts, warehouse vs source totals)
scripts/
└── load_source.sh        # Loads the six dump files in data/ into ecommerce_source
sql/                      # Warehouse setup scripts (schema, indexes)
tests/                    # Functional tests for ETL and reports
.env.example              # Template for environment variables (copy to .env)
docker-compose.yml        # MySQL container definition
pyproject.toml            # Project dependencies (managed with uv)
README.md
```

## Setup

Run all commands from the project root in PowerShell.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/), running
- The six source dump files 

### 1. Install uv

```powershell
pip install uv
```
 or 

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close and reopen the terminal, then check it:

```powershell
uv --version
```

### 2. Place the 6 sql dump files 

Paste the 6 files in the `/data` folder.

### 3. Install the project dependencies

```powershell
uv sync
```

This creates `.venv` and installs everything listed in `pyproject.toml`. 

### 4. Start MySQL

```powershell
docker compose up -d
docker compose ps
```

Wait until the status shows `healthy`. On first boot the init script creates `ecommerce_source` and gives the app user read-only access to it. `ecommerce_dw` is created automatically.

### 5. Load the source database (once)

```powershell
docker exec ecommerce-mysql sh /scripts/load_source.sh
```

This takes a few minutes.

## What You Should Have After Setup

After completing the steps above, your machine has:

| Component | State |
|---|---|
| `.venv` | Python environment with all dependencies installed |
| Docker container `ecommerce-mysql` | Running and `healthy` on port 3307 |
| Docker volume `mysql_data` | Stores the database files, so data survives restarts |
| Database `ecommerce_source` | Loaded with 6 tables: `Couriers`, `Riders`, `Users`, `Products`, `Orders`, `OrderItems` |
| Database `ecommerce_dw` | Created and **empty**, ready for the warehouse schema |

### Access rules

- `ecommerce_source` is **read-only** for the app user (`SELECT` only). The data can't be changed by the app or ETL.
- `ecommerce_dw` is **read/write** and disposable. It can be dropped and rebuilt at any time without touching the source.

### Quick check

```powershell
docker exec -it ecommerce-mysql mysql -u dw_user -p
```

```sql
SHOW DATABASES;               -- ecommerce_source, ecommerce_dw
USE ecommerce_source;
SHOW TABLES;                  -- the 6 source tables
SELECT COUNT(*) FROM Orders;
USE ecommerce_dw;
SHOW TABLES;                  -- empty for now
```

Table names are case-sensitive (`Orders`, not `orders`).

### To Implement

- Warehouse schema (`sql/`)
- ETL pipeline (`etl/`)
- OLAP queries and API endpoints (`app/`)

