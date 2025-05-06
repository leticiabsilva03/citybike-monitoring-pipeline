from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from minio import Minio
from io import BytesIO
import requests

def fetch_stations():
    client = Minio(
        "minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin123",
        secure=False
    )
    url = "https://api.citybik.es/v2/networks/citi-bike-nyc"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.content
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    payload = BytesIO(data)
    client.put_object(
        bucket_name="bronze",
        object_name=f"stations/{ts}.json",
        data=payload,
        length=len(data),
        content_type="application/json"
    )

with DAG(
    "bronze",
    start_date=datetime(2025,5,4),
    schedule_interval="*/5 * * * *",
    catchup=False
) as dag:
    fetch = PythonOperator(
        task_id="fetch_stations",
        python_callable=fetch_stations
    )
