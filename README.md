# CityBike Monitoring Pipeline

This project implements a real-time data pipeline for monitoring CityBike network stations using **Apache Airflow**, **MinIO**, and **Docker Compose**. Its goal is to ingest, process, and store station status across three layers — **Bronze**, **Silver**, and **Gold** — delivering data ready for analysis and visualization.

---

## 🚀 Pipeline Overview

This pipeline ingests station status and trip data (future extension) in three layers:

1. **Bronze**: Collector DAG fetches raw JSON snapshots every 5 minutes from the CityBik.es API and stores them in MinIO (`bronze/stations/{timestamp}.json`).
2. **Silver**: Transformer DAG normalizes the latest JSON, selects key fields (`id`, `name`, `latitude`, `longitude`, `empty_slots`, `free_bikes`, `timestamp`) and writes a Parquet file to MinIO (`silver/stations/{timestamp}.parquet`).
3. **Gold**: Aggregator DAG runs hourly, reads the last 24h of Parquet files, computes average available bikes and empty slots per station, and exports a CSV summary to MinIO (`gold/stations-summary/{timestamp}.csv`).

With this structure you get a clean, performant dataset ready for BI tools.

---

## 🚀 Technologies

* **Apache Airflow**: Orchestrates DAGs and tasks.
* **MinIO**: S3-compatible local Data Lake.
* **Docker Compose**: Manages containerized services.
* **Python**: Extraction and transformation scripts (`requests`, `boto3`, `pandas`).
* **GitHub Actions**: CI/CD pipelines, linting, and DAG validation.

---

## 🔧 Setup & Deployment

1. **Clone the repo**

   ```bash
   git clone https://github.com/leticiabsilva03/citybike-monitoring-pipeline.git
   cd citybike-monitoring-pipeline
   ```

2. **Install requirements**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure MinIO**

   * Create buckets: `bronze`, `silver`, `gold`
   * (Optional) Use `mc` CLI:

     ```bash
     mc alias set local http://localhost:9000 minioadmin minioadmin123
     mc mb local/bronze
     mc mb local/silver
     mc mb local/gold
     ```

4. **Airflow Setup**

   * Ensure `AIRFLOW_HOME` is set and your `dags_folder` points here.
   * Place all DAG files under `${AIRFLOW_HOME}/dags/`.
   * Configure an Airflow connection `minio_conn` (S3 type) with host `http://minio:9000`, access key `minioadmin`, secret key `minioadmin123`, and `{"aws_endpoint_url": "http://minio:9000"}` in Extras.

5. **Start Airflow**

   ```bash
   airflow db init
   airflow users create --username admin --password admin --role Admin --email you@example.com
   airflow scheduler &
   airflow webserver --port 8080
   ```

6. **Trigger DAGs**

   * **Bronze & Silver** run every 5 minutes automatically.
   * **Gold** runs hourly to refresh summary.

---

## 🗂 Repository Structure

```
citybike-monitoring-pipeline/
├── dags/
│   ├── collector_station_status.py   # Bronze DAG: fetch raw station snapshots
│   ├── silver.py                     # Silver DAG: normalize JSON to Parquet
│   └── gold.py                       # Gold DAG: aggregate data for reports
├── requirements.txt                  # Python dependencies
└── README.md                         # Project overview and usage
```

---

## 📊 Power BI Integration

Point Power BI Desktop to your MinIO S3 buckets:

1. **Amazon S3 Connector**: Use endpoint `http://localhost:9000`, enable path-style, and provide MinIO credentials.
2. **Web.Contents** in Power Query: for custom HTTP calls.

Load `gold/stations-summary/` CSVs to build maps, time-series, and heatmaps without complex modeling.

---

## 🛠️ Next Enhancements

* **Trip Data**: ingest Citi Bike trip CSVs into Bronze/Silver layers and build hourly departure/arrival summaries in Gold.
* **Holidays & Events**: enrich with Python `holidays` lib and custom event calendar to flag peaks.
* **User Profiles**: integrate demographic or weather data for deeper insights.

---

## 🤝 Contributing

Contributions welcome! Please open issues for suggestions or submit pull requests with improvements.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
