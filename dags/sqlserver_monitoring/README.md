# SQL Server Monitoring Platform

> An end-to-end SQL Server observability platform for monitoring database health, performance, storage, and resource utilization.

Built with **Apache Airflow, PostgreSQL, ClickHouse, Grafana, Docker, and Python**.

---

## 🚀 Overview

SQL Server Monitoring Platform collects and analyzes SQL Server metrics and provides historical monitoring through automated Airflow workflows and Grafana dashboards.

### Architecture

```text
                         SQL Server
                             │
                             ▼
                    ┌─────────────────┐
                    │  Apache Airflow │
                    │                 │
                    │  Sensors        │
                    │  Hooks          │
                    │  Operators      │
                    │  DAGs           │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        Server Metrics   Database Metrics  Performance
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                       ClickHouse
                             │
                             ▼
                         Grafana


                    PostgreSQL
                         │
                         ▼
                 Airflow Metadata
```

Airflow metadata is stored in **PostgreSQL**, while monitoring data is stored in **ClickHouse**. Airflow uses **LocalExecutor** for task execution.

---

## ✨ Features

### 🖥️ Server Monitoring

* CPU utilization
* Memory utilization
* Disk I/O
* Database connections
* Active sessions
* Server uptime
* Resource trends

### 🗄️ Database Monitoring

* Database inventory
* Database size
* Data file size
* Log file size
* Auto-growth configuration
* Recovery model
* Database state
* Storage growth

### 📊 Table & Index Monitoring

* Table inventory
* Row counts
* Data size
* Index size
* Index inventory
* Index fragmentation
* Index usage statistics
* Missing indexes
* Unused indexes

### ⚡ Performance Monitoring

* Wait statistics
* Blocking sessions
* Deadlocks
* Long-running queries
* Query execution metrics

### 🚨 Alerting

Monitoring metrics can be evaluated against configurable thresholds.

Examples:

```text
CPU > 90%
Memory > 90%
Disk usage > 85%
Index fragmentation > 30%
Blocking detected
Deadlock detected
Long-running query detected
```

---

## 🏗️ Technology Stack

| Technology | Purpose |
|---|---|
| 🐍 Python | Monitoring and data collection |
| 🛩️ Apache Airflow | Workflow orchestration |
| 🐘 PostgreSQL | Airflow metadata database |
| ⚙️ LocalExecutor | Task execution |
| 🏎️ ClickHouse | Monitoring data storage |
| 📈 Grafana | Visualization and dashboards |
| 🐳 Docker | Containerization |
| 🗄️ SQL Server | Monitoring target |

---

## 📂 Project Structure

```text
sqlserver-monitoring-platform/
│
├── airflow/
│   ├── dags/
│   ├── plugins/
│   │   ├── hooks/
│   │   ├── operators/
│   │   └── sensors/
│   ├── Dockerfile
│   └── requirements.txt
│
├── clickhouse/
│   ├── init/
│   └── config/
│
├── grafana/
│   ├── dashboards/
│   └── provisioning/
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── setup.sh
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/sqlserver-monitoring-platform.git
cd sqlserver-monitoring-platform
```

### 2. Configure Environment

```bash
cp .env.example .env
```

> `.env` is excluded from Git and should never be committed because it may contain credentials and secrets.

### 3. Start the Platform

```bash
chmod +x setup.sh
./setup.sh
```

The setup script automatically:

* Validates Docker
* Validates Docker Compose
* Creates `.env` if needed
* Generates the Airflow Fernet key
* Configures the current user ID
* Builds the Airflow image
* Initializes PostgreSQL
* Starts Airflow
* Starts ClickHouse
* Starts Grafana

---

## 🌐 Services

| Service         | URL                                            |
| --------------- | ---------------------------------------------- |
| Airflow         | [http://localhost:8081](http://localhost:8081) |
| Grafana         | [http://localhost:3001](http://localhost:3001) |
| ClickHouse HTTP | [http://localhost:8124](http://localhost:8124) |

Credentials are configured through `.env`.

---

## 🔄 Monitoring Pipeline

```text
SQL Server
     │
     ▼
Availability Check
     │
     ▼
Server Metrics
     │
     ├── CPU / Memory
     ├── Disk / I/O
     └── Connections
     │
     ▼
Database Metrics
     │
     ├── Database Size
     ├── Data / Log
     ├── Tables
     └── Indexes
     │
     ▼
Performance Metrics
     │
     ├── Fragmentation
     ├── Index Usage
     ├── Wait Statistics
     ├── Blocking
     └── Deadlocks
     │
     ▼
ClickHouse
     │
     ▼
Alert Evaluation
     │
     ▼
Grafana
```

---

## 📈 Observability

The platform is designed to provide historical SQL Server observability and help answer questions such as:

* How much CPU and memory is SQL Server using?
* Which database consumes the most storage?
* Which tables are growing fastest?
* Which indexes have high fragmentation?
* Which indexes are not being used?
* Are blocking sessions occurring?
* Are deadlocks increasing?
* How is database size changing over time?

---

## 🗺️ Roadmap

### Core

- [x] Server Resource Monitoring
- [x] Database Inventory
- [x] Database / Data / Log Size
- [x] Table & Index Inventory
- [x] Fragmentation Monitoring
- [x] Index Usage Monitoring
- [x] Historical Metrics
- [x] Alert Evaluation

### Advanced Monitoring

- [ ] Wait Statistics
- [ ] Blocking Analysis
- [ ] Deadlock Monitoring
- [ ] Long-Running Query Detection
- [ ] SQL Server Health Score
- [ ] Multi-Server Monitoring

### Future

- [ ] Root Cause Analysis
- [ ] Capacity Planning
- [ ] Incident Playback
- [ ] Query Tuning
- [ ] AI-powered SQL Server Assistant
- [ ] AI-powered Root Cause Analysis

---

## 🛠️ Development

Build the containers:

```bash
docker compose build
```

Start the platform:

```bash
docker compose up -d
```

Check services:

```bash
docker compose ps
```

View Airflow logs:

```bash
docker logs airflow_webserver
```

View scheduler logs:

```bash
docker logs airflow_scheduler
```

Stop the platform:

```bash
docker compose down
```

---

## 🔐 Security

Do not commit `.env` to Git.

Use strong credentials for production environments and replace all default passwords.

---

## 🤝 Contributing

Contributions, ideas, bug reports, and feature requests are welcome.

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/my-feature
```

3. Commit your changes

```bash
git commit -m "Add my feature"
```

4. Push the branch

```bash
git push origin feature/my-feature
```

5. Open a Pull Request

---

## 📜 License

This project is currently intended for educational, development, and portfolio purposes.

A formal open-source license may be added in the future.

---

## 👩‍💻 Author

**Sara**

Data Engineer

**Data Engineering • SQL Server • Apache Airflow • Docker • Observability**

---

## ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub.

> Built to turn SQL Server monitoring into a structured, automated, and observable data platform.

