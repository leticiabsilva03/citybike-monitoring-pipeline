# dags/silver.py

import minio  # type: ignore
import yaml  # type: ignore
import pandas as pd  # type: ignore

from airflow.decorators import dag, task  # type: ignore
from datetime import datetime, timedelta

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": "leticiabscoding@gmail.com",
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

START_DATE = datetime(2025, 1, 1)


@dag(
    dag_id="silver_dag",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2025, 1, 1),
    schedule="@hourly",
    catchup=False,
    tags=["etl", "silver"],
)
def silver():
    @task()
    def extract_bronze() -> pd.DataFrame:
        client = minio.Minio("play.min.io", access_key="...", secret_key="...")
        obj = client.get_object("bronze-bucket", "bronze.parquet")
        df = pd.read_parquet(obj)
        return df

    @task()
    def transform(df: pd.DataFrame) -> pd.DataFrame:
        _ = yaml.safe_load(open("transform-config.yml", "r"))
        # ...aplica transformações com cfg...
        return df

    @task(multiple_outputs=True)
    def load_silver(df: pd.DataFrame) -> dict:
        client = minio.Minio("play.min.io", access_key="...", secret_key="...")
        data = df.to_parquet()
        client.put_object(
            bucket_name="silver-bucket",
            object_name="silver.parquet",
            data=data,
            length=len(data),
            content_type="application/octet-stream",
        )
        return {"bucket": "silver-bucket", "key": "silver.parquet"}

    return extract_bronze() >> transform() >> load_silver()


silver_dag = silver()
