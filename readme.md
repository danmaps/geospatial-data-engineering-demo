# Geospatial Data Engineering Demo

An end-to-end **cloud + SQL pipeline** that ingests utility asset data and external fire-risk layers, transforms them with **PostgreSQL/PostGIS**, orchestrates workflows with a scheduler, and serves outputs to a lightweight **Streamlit dashboard**.

This project demonstrates how geospatial automation skills can be applied in a **data engineering context**: ETL pipelines, SQL transformations, cloud orchestration, and reproducible analytics.

---

## 📐 Architecture

```text
[Utility Assets]     [External Fire Risk Data]
   |                         |
   v                         v
Blob/S3 (raw landing zone, CSV/GeoJSON)
   |
   v
Postgres + PostGIS  <- SQL transforms + QA
   |
   v
Gold tables & materialized views
   |
 ┌───────────────┬──────────────────────┐
 | Streamlit app | Exports (CSV/GeoJSON)|
 └───────────────┴──────────────────────┘

```

---

## 🗂 Tech Stack

- **Database**: PostgreSQL 15 + PostGIS 3
- **Orchestration**: Azure Data Factory (or Apache Airflow locally)
- **Storage**: Azure Blob Storage / AWS S3 (raw + processed)
- **Compute**: Databricks Community Edition (optional scale-out)
- **App**: Streamlit for dashboard
- **Languages**: Python, SQL
- **Infra**: Docker for local Postgres; Terraform templates (optional)  

---

## 🚀 Quick Start (local demo)


1. **Bring up Postgres with PostGIS**

   ```bash
   docker compose up -d
   ```


2. **Initialize database**

   ```bash
   psql -h localhost -U postgres -f sql/00_init_postgis.sql
   ```


3. **Load sample data**

   ```bash
   python etl/ingest_assets.py
   python etl/ingest_risk.py
   ```


4. **Run transforms**

   ```bash
   psql -h localhost -U postgres -d utility -f sql/10_transform_assets.sql
   psql -h localhost -U postgres -d utility -f sql/20_join_assets_risk.sql
   ```



5. **Launch dashboard**

   ```bash
   streamlit run app/dashboard.py
   ```

---


## 🐍 Setting Up a Python Virtual Environment

It is recommended to use a virtual environment for Python dependencies:

1. Open a terminal in the project root.
2. Create a new virtual environment:

   ```cmd
   python -m venv .venv
   ```

3. Activate the environment (Windows cmd):

   ```cmd
   .venv\Scripts\activate
   ```

4. Install dependencies (e.g., Streamlit):

   ```cmd
   pip install streamlit
   ```

You can now run Python scripts and the Streamlit app in this isolated environment.

---

## ▶️ Running the Streamlit App

## 🔧 Environment Configuration

The project reads database settings from environment variables (see `.env.example`). To use them:

1. Copy the example file:
   ```cmd
   copy .env.example .env
   ```
2. (Optional) Edit credentials in `.env`.
3. Ensure `python-dotenv` is installed (add to dev deps if needed).
4. Run any ETL script; it will automatically load `.env` and connect.

Key variables:
```
DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, EXPORT_DIR
```

Example running an ingestion:
```cmd
python etl\ingest_assets.py
python etl\ingest_risk.py
python etl\publish_exports.py
```

The export script writes CSVs to the `EXPORT_DIR` (default `data/processed`).

To launch the dashboard:

1. Make sure you have Python 3.8+ and Streamlit installed:

   ```bash
   pip install streamlit
   ```

2. Run the app from the project root:

   ```bash
   streamlit run app/dashboard.py
   ```

3. The dashboard will open in your browser at [http://localhost:8501](http://localhost:8501).

**Troubleshooting:**
- If you see a `ModuleNotFoundError`, ensure you are in the correct virtual environment and dependencies are installed.
- If the app does not open, check for errors in the terminal and verify the file path.

---

## 📂 Repository Layout

```
.
├─ app/
│  └─ dashboard.py           # Streamlit dashboard
├─ data/
│  ├─ raw/                   # raw inputs
│  ├─ processed/             # outputs
│  └─ catalog.md             # dataset notes
├─ etl/
│  ├─ ingest_assets.py       # loads utility asset data
│  ├─ ingest_risk.py         # loads fire risk data
│  └─ publish_exports.py     # exports gold tables
├─ sql/
│  ├─ 00_init_postgis.sql
│  ├─ 10_transform_assets.sql
│  └─ 20_join_assets_risk.sql
├─ orchestration/
│  ├─ adf_pipeline.json      # Azure Data Factory template
│  └─ schedules.md
├─ infra/
│  ├─ docker-compose.yml     # local DB + pgAdmin
│  └─ manual_setup.md
└─ tests/
   ├─ test_sql_quality.sql
   └─ test_python_etl.py
```

---

## 🔑 Key SQL Examples

```sql
-- Transform raw poles into core schema
create table core.poles as
select id,
       install_year,
       status,
       st_setsrid(st_makepoint(lon, lat), 4326) as geom
from staging.poles_raw
where status in ('active','planned');

-- Join poles to fire zones
create materialized view mart.poles_fire_risk as
select p.id,
       r.zone_id,
       r.risk_score,
       p.install_year
from core.poles p
join risk.fire_zones r
  on st_intersects(p.geom, r.geom);
```

---

## ✅ Data Quality & Observability

- Row counts before/after each stage
- `NOT NULL` + geometry checks in SQL
- Run log table (`ops.run_log`) with pipeline, step, status, row counts, duration
- Unit tests for ETL scripts and SQL checks

---

## 📊 Dashboard

The Streamlit app provides:

- Risk summary by zone (count, average score)
- Sample of joined assets + zones
- Simple data export to CSV/GeoJSON

---

## 📈 Results

- Automated daily refresh possible with ADF/Airflow
- Materialized views for fast queries
- Spatial indexes (GIST) accelerate joins
- Exportable datasets for downstream BI tools (Power BI, Tableau, etc.)

---

## 🔮 Roadmap

- Incremental data loads by date
- API endpoint to serve gold tables
- Add Spark job for large-area joins
- CI/CD workflow for ETL tests

---

## 📄 License

MIT License. Public datasets used for demo purposes only.

