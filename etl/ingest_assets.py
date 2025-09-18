"""Ingest utility asset CSV into staging then promote to core."""
from pathlib import Path
import csv
import psycopg2
from config import load_settings, get_connection

ASSETS_CSV = Path("data/raw/utility_assets.csv")

def ensure_tables(cur):
    cur.execute("""
        create schema if not exists staging;
        create schema if not exists core;
        create table if not exists staging.poles_raw(
            id integer primary key,
            install_year integer,
            status text,
            lon double precision,
            lat double precision
        );
        create table if not exists core.poles(
            id integer primary key,
            install_year integer,
            status text,
            geom geometry(Point,4326)
        );
    """)

def load_raw(cur):
    if not ASSETS_CSV.exists():
        raise FileNotFoundError(f"Missing {ASSETS_CSV}")
    cur.execute("truncate staging.poles_raw;")
    with ASSETS_CSV.open() as f:
        reader = csv.DictReader(f)
        rows = [(
            int(r["id"]), int(r["install_year"]), r["status"], float(r["lon"]), float(r["lat"])
        ) for r in reader]
    cur.executemany(
        "insert into staging.poles_raw(id,install_year,status,lon,lat) values (%s,%s,%s,%s,%s)",
        rows,
    )
    return len(rows)

def promote(cur):
    cur.execute("""
        insert into core.poles as t(id, install_year, status, geom)
        select id, install_year, status, st_setsrid(st_makepoint(lon,lat),4326)
        from staging.poles_raw
        on conflict (id) do update set
            install_year=excluded.install_year,
            status=excluded.status,
            geom=excluded.geom;
    """)

def main():
    settings = load_settings()
    with get_connection() as conn:
        with conn.cursor() as cur:
            ensure_tables(cur)
            inserted = load_raw(cur)
            promote(cur)
    print(f"Loaded {inserted} asset rows into core.poles")

if __name__ == "__main__":  # pragma: no cover
    main()
