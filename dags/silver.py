from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from minio import Minio
import json
import pandas as pd
from io import BytesIO

def transform_stations():
    client = Minio(
        "minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin123",
        secure=False
    )

    # Lista arquivos mais recentes do bucket bronze
    objects = client.list_objects("bronze", prefix="stations/", recursive=True)
    latest_obj = max(objects, key=lambda obj: obj.last_modified)

    # Baixa o conteúdo do JSON bruto
    response = client.get_object("bronze", latest_obj.object_name)
    raw_data = json.load(response)

    # Transforma os dados em DataFrame
    stations = raw_data["network"]["stations"]
    df = pd.DataFrame(stations)

    # Aqui você pode filtrar/normalizar dados, se necessário
    # Exemplo: selecionando apenas algumas colunas
    df = df[["id", "name", "latitude", "longitude", "empty_slots", "free_bikes", "timestamp"]]

    # Salva como Parquet (ou CSV) no bucket silver
    buffer = BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)

    silver_path = latest_obj.object_name.replace("stations/", "").replace(".json", ".parquet")
    client.put_object(
        bucket_name="silver",
        object_name=f"stations/{silver_path}",
        data=buffer,
        length=buffer.getbuffer().nbytes,
        content_type="application/octet-stream"
    )

with DAG(
    "silver",
    start_date=datetime(2025,5,4),
    schedule_interval="*/5 * * * *",
    catchup=False
) as dag:
    transform = PythonOperator(
        task_id="transform_stations",
        python_callable=transform_stations
    )
