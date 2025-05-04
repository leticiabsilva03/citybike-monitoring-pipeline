# citybike-monitoring-pipeline
End-to-end data pipeline for Citi Bike station status: ingest JSON snapshots with Airflow, store raw data in MinIO, transform with PySpark into Parquet, model in PostgreSQL star schema, and surface real‑time dashboards with Power BI and Grafana.
