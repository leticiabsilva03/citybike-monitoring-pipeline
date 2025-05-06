# CityBike Monitoring Pipeline

This project implements a real-time data pipeline for monitoring CityBike network stations using **Apache Airflow**, **MinIO**, and **Docker Compose**. Its goal is to ingest, process, and store station status across three layers — **Bronze**, **Silver**, and **Gold** — delivering data ready for analysis and visualization.

---

## 📦 Project Architecture

* **Bronze**: Captures and stores raw JSON snapshots of station data.
* **Silver**: Transforms raw JSON into normalized Parquet tables.
* **Gold**: Aggregates metrics and prepares datasets for dashboards and reports.

---

## 🚀 Technologies

* **Apache Airflow**: Orchestrates DAGs and tasks.
* **MinIO**: S3-compatible local Data Lake.
* **Docker Compose**: Manages containerized services.
* **Python**: Extraction and transformation scripts (`requests`, `boto3`, `pandas`).
* **GitHub Actions**: CI/CD pipelines, linting, and DAG validation.

---

## 🔧 Prerequisites

1. Docker & Docker Compose
2. (Optional) Python 3.8+ for local testing and notebooks

---

## 🛠️ Installation & Execution Guide

1. **Clone the repository**

   ```bash
   git clone https://github.com/leticiabsilva03/citybike-monitoring-pipeline.git
   cd citybike-monitoring-pipeline
   ```

2. **Set environment variables**
   Create a `.env` file with:

   ```env
   MINIO_ROOT_USER=minio
   MINIO_ROOT_PASSWORD=minio123
   ```

3. **Start the services**

   ```bash
   docker-compose up -d
   ```

4. **Access the UIs**

   * Airflow: `http://localhost:8080`
   * MinIO:   `http://localhost:9000` (user: `minio`, password: `minio123`)

5. **Create the Bronze bucket**
   In the MinIO console, click **Create Bucket** and name it `bronze`.

6. **Trigger the Bronze DAG**
   In the Airflow UI, enable and trigger the `station_status_bronze` DAG.
   Verify the presence of JSON files under `bronze/stations/` in MinIO.

---

## 📁 Directory Structure

```text
├── dags/                   # Airflow DAG definitions
│   └── station_status_bronze.py
├── .github/workflows/      # CI/CD pipelines
├── data/                   # Persistent volume for MinIO
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## 📊 Next Phases

1. **Silver**: Normalize raw JSON into Parquet tables following a defined schema.
2. **Gold**: Aggregate data, load into a relational database, and build interactive dashboards.

---

## 🤝 Contributing

Contributions welcome! Please open issues for suggestions or submit pull requests with improvements.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
