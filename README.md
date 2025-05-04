# CityBike Monitoring Pipeline (WIP)

> **Status:** In Development – initial environment setup and Bronze ingestion layer implemented.

---

## 🚧 Project Overview

An end-to-end data pipeline for Citi Bike station status snapshots. Currently, I have completed:

* **Environment & Infrastructure**: Docker Compose setup with MinIO, PostgreSQL, and Airflow.
* **Bronze Layer**: Airflow DAG to fetch JSON snapshots from the CityBikes API every 5 minutes and store them in MinIO under `bronze/stations/`.

Work on Silver (data transformation) and Gold (analytics model) layers, as well as dashboards, is planned for upcoming sprints.

---

## 🛠️ What’s Done So Far

1. **Docker Compose**
   * Services: MinIO (local S3), PostgreSQL (for future use), Airflow.
2. **MinIO Bucket**
   * Created `bronze` bucket to store raw JSON.
3. **Airflow DAG**
   * `station_status_bronze`: PythonOperator fetches data from `https://api.citybik.es/v2/networks/citi-bike-nyc` every 5 minutes.
   * Saves JSON files named by UTC timestamp.

---

## 📦 Prerequisites

* Docker & Docker Compose installed
* Python 3.8+ (for Airflow DAG requirements)
* MinIO Client (`mc`) for bucket management

---

## 🔧 Local Setup & Bronze Ingestion

1. **Clone Repo**

   ```bash
   git clone https://github.com/your-username/citybike-monitoring-pipeline.git
   cd citybike-monitoring-pipeline
   ```

2. **Start Services**

   ```bash
   docker-compose up -d
   ```

3. **Create MinIO Bucket**

   ```bash
   mc alias set local http://localhost:9000 minio minio123
   mc mb local/bronze
   ```
---

## 📅 Next Steps

* **Silver Layer**: Build data transformation job (PySpark) to normalize and write Parquet files.
* **Gold Layer**: Load curated data into PostgreSQL star schema.
* **Dashboards**: Create Power BI/Metabase dashboard for station availability trends.
* **Monitoring & Alerts**: Set up Prometheus/Grafana for pipeline metrics.

---

## 📁 Project Structure

```
citybike-monitoring-pipeline/
├── dags/                   # Airflow DAGs (Bronze ingestion)
├── infra/                  # (Planned) Terraform for local infra
├── docker-compose.yml      # MinIO, PostgreSQL, Airflow
├── .gitignore              # Ignored files
└── README.md               # This file (WIP)
```

---

## 🤝 Contributing

This project is early in development. Contributions and feedback on the Bronze layer are welcome! Open issues or PRs for improvements.

---

*Last updated: May 4, 2025*
