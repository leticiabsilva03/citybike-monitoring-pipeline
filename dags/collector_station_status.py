# dags/collector_station_status.py

import minio  # type: ignore
import yaml  # type: ignore
import json
from great_expectations.dataset import PandasDataset  # type: ignore

from airflow.decorators import dag, task  # type: ignore
from datetime import datetime, timedelta

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

START_DATE = datetime(2025, 1, 1)


@dag(
    dag_id="collector_station_status",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2025, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
    tags=["collector", "status"],
)
def collector_station_status():
    @task()
    def fetch_status() -> list:
        client = minio.Minio("play.min.io", access_key="...", secret_key="...")
        obj = client.get_object("source-bucket", "stations.json")
        data = yaml.safe_load(obj)
        if "network" not in data or "stations" not in data["network"]:
            raise ValueError("Resposta inválida")
        return data["network"]["stations"]

    @task()
    def validate_status(stations: list) -> list:
        batch = PandasDataset({"stations": stations})
        batch.expect_table_row_count_to_be_between(min_value=1, max_value=None)
        batch.expect_column_to_exist("stations")
        res = batch.validate()
        if not res.success:
            raise ValueError("Validação falhou")
        return stations

    @task()
    def save_to_minio(stations: list):
        client = minio.Minio("play.min.io", access_key="...", secret_key="...")
        today = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        path = f"collector/{today}.json"
        content = json.dumps({"stations": stations, "ts": today}).encode()
        client.put_object(
            bucket_name="collector-bucket",
            object_name=path,
            data=content,
            length=len(content),
            content_type="application/json",
        )

    return fetch_status() >> validate_status() >> save_to_minio()


collector_station_status_dag = collector_station_status()
