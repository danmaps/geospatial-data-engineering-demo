"""Ingest fire risk GeoJSON polygons into risk.fire_zones."""
import json
from pathlib import Path
from config import get_connection, load_settings

RISK_GEOJSON = Path("data/raw/fire_risk_zones.geojson")

def ensure_table(cur):
    cur.execute("""
        create schema if not exists risk;
        create table if not exists risk.fire_zones(
            zone_id integer primary key,
            risk_score double precision,
            geom geometry(Polygon,4326)
        );
    """)

def load_geojson(cur):
    if not RISK_GEOJSON.exists():
        raise FileNotFoundError(f"Missing {RISK_GEOJSON}")
    data = json.loads(RISK_GEOJSON.read_text())
    cur.execute("truncate risk.fire_zones;")
    rows = []
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        zone_id = int(props.get("zone_id"))
        risk_score = float(props.get("risk_score", 0.0))
        geom_json = json.dumps(feat.get("geometry"))
        rows.append((zone_id, risk_score, geom_json))
    cur.executemany(
        """
        insert into risk.fire_zones(zone_id, risk_score, geom)
        values (%s,%s, st_setsrid(st_geomfromgeojson(%s),4326))
        on conflict (zone_id) do update set risk_score=excluded.risk_score,
            geom=excluded.geom
        """,
        rows,
    )
    return len(rows)

def main():
    load_settings()
    with get_connection() as conn:
        with conn.cursor() as cur:
            ensure_table(cur)
            count = load_geojson(cur)
    print(f"Loaded {count} fire risk zones into risk.fire_zones")

if __name__ == "__main__":  # pragma: no cover
    main()
