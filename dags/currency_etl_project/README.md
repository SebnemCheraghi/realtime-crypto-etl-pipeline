# Real-Time Crypto ETL & DataOps Pipeline

An enterprise-grade, containerized data pipeline built to ingest, process, orchestrate, and visualize high-frequency cryptocurrency data.

## 🚀 Tech Stack
- **Orchestration:** Apache Airflow
- **Data Ingestion:** Python (REST APIs, Custom Operators)
- **Data Warehouse:** ClickHouse (Columnar Storage)
- **Visualization & Monitoring:** Grafana (v12)
- **Infrastructure:** Docker & Docker Compose

## 📊 Architecture Flow
1. **Extraction:** Apache Airflow triggers DAGs to fetch real-time cryptocurrency data from financial APIs.
2. **Ingestion & Storage:** Cleaned data is loaded into a high-performance **ClickHouse** database.
3. **Visualization:** **Grafana** connects natively to ClickHouse to render real-time analytics and monitoring dashboards.

## 🛠️ Quick Start
1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/currency_etl_project.git](https://github.com/SebnemCheraghi/currency_etl_project.git)
   cd currency_etl_project

   Spin up the infrastructure using Docker Compose:
   docker-compose up -d