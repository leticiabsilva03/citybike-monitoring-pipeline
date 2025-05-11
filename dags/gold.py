from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from minio import Minio
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta, timezone


def build_gold_summary():
    client = Minio("minio:9000", access_key="minioadmin",
                   secret_key="minioadmin123", secure=False)

    # 1) Lista arquivos silver das últimas 24h
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    objs = client.list_objects("silver", prefix="stations/", recursive=True)
    recent = [o for o in objs if o.last_modified >= cutoff]

    # 2) Lê todos eles em um único DataFrame
    dfs = []
    for obj in recent:
        resp = client.get_object("silver", obj.object_name)
        df = pd.read_parquet(BytesIO(resp.read()))
        dfs.append(df)
    full = pd.concat(dfs, ignore_index=True)

    # 3) Agregação: disponibilidade média de bikes por estação
    summary = (full
               .groupby(["id", "name", "latitude", "longitude"])
               .agg({
                   "free_bikes": "mean",
                   "empty_slots": "mean"
               })
               .reset_index()
               .rename(columns={
                   "free_bikes": "avg_free_bikes",
                   "empty_slots": "avg_empty_slots"
               }))
    
    # 4) Exporta para CSV
    buf = BytesIO()
    summary.to_csv(buf, index=False)
    buf.seek(0)
    
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    client.put_object(
        bucket_name="gold",
        object_name=f"stations-summary/{ts}.csv",
        data=buf,
        length=buf.getbuffer().nbytes,
        content_type="text/csv"
    )

with DAG(
    "gold",
    start_date=datetime(2025, 5, 4),
    schedule_interval="0 * * * *",  # a cada hora, por exemplo
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)}
) as dag:
    gold = PythonOperator(
        task_id="build_gold_summary",
        python_callable=build_gold_summary
    )

    gold
