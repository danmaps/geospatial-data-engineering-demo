from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG("utility_risk_pipeline", start_date=datetime(2025,1,1), schedule="@daily", catchup=False) as dag:
    init = BashOperator(task_id="init_postgis", bash_command="psql -h $PGHOST -U $PGUSER -d $PGDB -f sql/00_init_postgis.sql")
    ingest_assets = BashOperator(task_id="ingest_assets", bash_command="python etl/ingest_assets.py")
    ingest_risk = BashOperator(task_id="ingest_risk", bash_command="python etl/ingest_risk.py")
    t_assets = BashOperator(task_id="transform_assets", bash_command="psql -h $PGHOST -U $PGUSER -d $PGDB -f sql/10_transform_assets.sql")
    join_risk = BashOperator(task_id="join_assets_risk", bash_command="psql -h $PGHOST -U $PGUSER -d $PGDB -f sql/20_join_assets_risk.sql")
    export = BashOperator(task_id="publish_exports", bash_command="python etl/publish_exports.py")
    init >> [ingest_assets, ingest_risk] >> t_assets >> join_risk >> export
