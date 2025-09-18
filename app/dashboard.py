import os, psycopg2, pandas as pd, streamlit as st

DB=dict(
    host=os.getenv("PGHOST","localhost"), dbname=os.getenv("PGDB","utility"),
    user=os.getenv("PGUSER","postgres"), password=os.getenv("PGPASSWORD","postgres"), port=int(os.getenv("PGPORT",5432))
)

@st.cache_data(ttl=60)
def q(sql, params=None):
    with psycopg2.connect(**DB) as conn:
        return pd.read_sql(sql, conn, params=params)

st.set_page_config(page_title="Utility Risk Pipeline", layout="wide")
st.title("Utility Risk Pipeline")
zone = st.text_input("Filter by zone_id (optional)","")

base_sql = """
select zone_id, count(*) as pole_count, avg(risk_score)::numeric(6,3) as avg_risk
from mart.poles_fire_risk
where (%s = '' or zone_id = %s)
group by zone_id order by avg_risk desc limit 100;
"""
df = q(base_sql, (zone, zone))
st.metric("Rows returned", len(df))
st.dataframe(df, use_container_width=True)

st.subheader("Latest sample")
sample_sql = "select id, zone_id, risk_score, install_year from mart.poles_fire_risk limit 200;"
st.dataframe(q(sample_sql), use_container_width=True)
