import os, psycopg2, pandas as pd
OUT=os.getenv("OUT_DIR","data/processed"); os.makedirs(OUT, exist_ok=True)
conn=psycopg2.connect(
    host=os.getenv("PGHOST","localhost"), dbname=os.getenv("PGDB","utility"),
    user=os.getenv("PGUSER","postgres"), password=os.getenv("PGPASSWORD","postgres"), port=int(os.getenv("PGPORT",5432))
)
df=pd.read_sql("select * from mart.poles_fire_risk", conn)
df.to_csv(f"{OUT}/poles_fire_risk.csv", index=False)
print(f"Wrote {len(df)} rows")
