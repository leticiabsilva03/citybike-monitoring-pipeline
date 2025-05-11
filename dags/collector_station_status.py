from airflow.decorators import dag, task
from datetime import datetime, timedelta, timezone
from minio import Minio
from io import BytesIO
import requests
import logging
import json
import yaml
import os

# == Carrega pipeline_config apenas do config.yaml ==
project_root = os.path.dirname(os.path.dirname(__file__))
with open(os.path.join(project_root, "config.yaml")) as f:
    pipeline_config = yaml.safe_load(f)

# == default_args ==
default_args = {
    "owner": "leticia",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["leticiabscoding@gmail.com"],
    "sla": timedelta(minutes=30),
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dag(
    dag_id="bronze",
    default_args=default_args,
    start_date=datetime(2025, 5, 4),
    schedule_interval="*/5 * * * *",
    catchup=False,
    doc_md="""
#### DAG Bronze CityBike
- Ingestão a cada 5 minutos
- Validação inline de schema
- Particionamento date-based
- Idempotência no MinIO
""",
)
def bronze_pipeline():
    @task
    def obter_dados_api():
        url = "https://api.citybik.es/v2/networks/citi-bike-nyc"
        logger.info(f"Buscando dados da URL: {url}")
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("network") or not data["network"].get("stations"):
            raise ValueError("Dados inválidos ou ausentes na resposta da API.")
        return {"data": data, "url": url}

    @task
    def validar_dados(payload: dict):
        from great_expectations.dataset import PandasDataset

        df = payload["data"]["network"]["stations"]
        batch = PandasDataset({"stations": df})
        batch.expect_table_row_count_to_be_between(min_value=1, max_value=None)
        batch.expect_column_to_exist("stations")
        res = batch.validate()
        if not res.success:
            logger.error("Falha na validação: %s", res)
            raise ValueError("Validação GE falhou")
        return payload

    @task
    def salvar_no_minio(payload: dict):
        minio_conf = pipeline_config["minio"]
        client = Minio(
            minio_conf["host"],
            access_key=minio_conf["access_key"],
            secret_key=minio_conf["secret_key"],
            secure=False,
        )
        data = payload["data"]
        fonte = payload["url"]
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        now = datetime.now(timezone.utc)
        prefix_tpl = pipeline_config["bronze"]["prefix"]
        prefix = prefix_tpl.format(
            year=now.year, month=f"{now.month:02d}", day=f"{now.day:02d}"
        )
        path = f"{prefix}/{ts}.json"

        record = {"ingestao": ts, "fonte": fonte, "dados": data}
        content = json.dumps(record).encode()

        try:
            client.stat_object(pipeline_config["bronze"]["bucket"], path)
            logger.info("Arquivo já existe: %s", path)
        except Exception:
            logger.info("Upload: %s/%s", pipeline_config["bronze"]["bucket"], path)
            client.put_object(
                bucket_name=pipeline_config["bronze"]["bucket"],
                object_name=path,
                data=BytesIO(content),
                length=len(content),
                content_type="application/json",
            )
            logger.info("Upload concluído: %s", path)

    dados = obter_dados_api()
    validados = validar_dados(dados)
    salvar_no_minio(validados)


dag = bronze_pipeline()
