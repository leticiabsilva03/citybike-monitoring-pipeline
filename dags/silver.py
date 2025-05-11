from airflow.decorators import dag, task
from datetime import datetime, timedelta, timezone
from minio import Minio
from io import BytesIO
import json
import yaml
import os
import logging
import pandas as pd

# == Carrega pipeline_config apenas do config.yaml ==
project_root = os.path.dirname(os.path.dirname(__file__))
with open(os.path.join(project_root, "config.yaml")) as f:
    pipeline_config = yaml.safe_load(f)

# == default_args ==
default_args = {
    "owner": "leticia",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["leticiabscoding@gmail.com"],
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dag(
    dag_id="silver",
    default_args=default_args,
    start_date=datetime(2025, 5, 10),
    schedule_interval="@hourly",
    catchup=False,
    doc_md="""
### DAG Silver CityBike
- Lista arquivos JSON na camada Bronze
- Processa e valida esquema e tipos via Great Expectations
- Normaliza JSON para tabular
- Salva CSV particionado no bucket Silver
"""
)
def silver_pipeline():
    @task
    def listar_arquivos_bronze():
        conf = pipeline_config["minio"]
        client = Minio(
            conf["host"],
            access_key=conf["access_key"],
            secret_key=conf["secret_key"],
            secure=False
        )
        bucket = pipeline_config["bronze"]["bucket"]
        prefix = pipeline_config["bronze"]["prefix"].split("{year}")[0].rstrip('/')
        objetos = client.list_objects(bucket, prefix=prefix, recursive=True)
        arquivos = [obj.object_name for obj in objetos if obj.object_name.endswith('.json')]
        logger.info(f"Arquivos encontrados no Bronze: {arquivos}")
        return arquivos

    @task
    def processar_e_salvar(arquivos: list):
        conf = pipeline_config["minio"]
        client = Minio(
            conf["host"],
            access_key=conf["access_key"],
            secret_key=conf["secret_key"],
            secure=False
        )
        silver_bucket = pipeline_config["silver"]["bucket"]
        silver_prefix = pipeline_config["silver"]["prefix"]

        for arquivo in arquivos:
            logger.info(f"Lendo JSON do Bronze: {arquivo}")
            response = client.get_object(bucket_name=pipeline_config["bronze"]["bucket"], object_name=arquivo)
            payload = json.load(response)

            df = pd.json_normalize(payload["dados"]["network"]["stations"])

            ts = payload.get("ingestao")
            dt = datetime.strptime(ts, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)

            from great_expectations.dataset import PandasDataset
            gedf = PandasDataset(df)
            gedf.expect_table_row_count_to_be_between(min_value=1, max_value=None)
            for col in ["id", "name", "latitude", "longitude"]:
                gedf.expect_column_to_exist(col)
            gedf.expect_column_values_to_not_be_null("id")
            gedf.expect_column_values_to_be_of_type("latitude", "float")
            gedf.expect_column_values_to_be_between("latitude", -90, 90)
            gedf.expect_column_values_to_be_between("longitude", -180, 180)
            res = gedf.validate()
            if not res.success:
                logger.error(f"Validação falhou para {arquivo}: {res}")
                raise ValueError("Falha na validação dos dados Silver.")

            prefix = silver_prefix.format(year=dt.year, month=f"{dt.month:02d}", day=f"{dt.day:02d}")
            csv_path = f"{prefix}/{ts}.csv"
            buf = BytesIO()
            df.to_csv(buf, index=False)
            buf.seek(0)

            client.put_object(
                bucket_name=silver_bucket,
                object_name=csv_path,
                data=buf,
                length=buf.getbuffer().nbytes,
                content_type="text/csv"
            )
            logger.info(f"CSV salvo no Silver: {silver_bucket}/{csv_path}")

    arquivos = listar_arquivos_bronze()
    processar_e_salvar(arquivos)

dag = silver_pipeline()
