from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from minio import Minio
import requests, json

def fetch_stations():
    client = Minio(
        "localhost:9000",
        access_key="minio",
        secret_key="minio123",
        secure=False
    )
    url = "https://api.citybik.es/v2/networks/citi-bike-nyc"
    data = requests.get(url).json()
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    payload = json.dumps(data).encode('utf-8')
    client.put_object("bronze", f"stations/{ts}.json", payload, len(payload))

with DAG(
    "station_status_bronze",
    start_date=datetime(2025,5,4),
    schedule_interval="*/5 * * * *",
    catchup=False
) as dag:
    fetch = PythonOperator(
        task_id="fetch_stations",
        python_callable=fetch_stations
    )
