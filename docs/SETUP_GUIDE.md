# Developer Setup & Local Execution Guide

This guide walks you through setting up, running, testing, and verifying the Chronicle Data Ingestion & Analytics Platform on macOS, Linux, or Windows.

---

## 1. System Requirements

* **Python**: 3.12+ (tested through 3.14)
* **PostgreSQL**: 15+ (or Docker Compose; zero-config SQLite is included by default for development)
* **Git**
* **Docker & Docker Compose** (optional for containerized deployment)

---

## 2. Quickstart with Virtual Environment (Zero Setup)

### Step 1: Clone and Enter Directory
```bash
git clone https://github.com/Spidey173/Chronicle.git
cd Chronicle
```

### Step 2: Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the example environment configuration:
```bash
cp .env.example .env
```
*(By default, `.env` uses SQLite `sqlite:///./data/analytics.db` allowing immediate local execution without spinning up PostgreSQL).*

### Step 5: Initialize Database & Run Migrations
```bash
python -m app.cli init
alembic upgrade head
```

### Step 6: Generate Sample Data & Ingest All Batches
```bash
python sample_data/generator.py
python -m app.cli run-all-samples
```

### Step 7: View Analytics in Terminal
```bash
python -m app.cli show-analytics
```

### Step 8: Start FastAPI Web Application & Interactive Dashboard
```bash
python -m app.cli start-server --reload
```
Open your browser at:
* **Interactive Dashboard**: `http://localhost:8000/` or `http://localhost:8000/dashboard`
* **Swagger OpenAPI Docs**: `http://localhost:8000/docs`
* **ReDoc Specifications**: `http://localhost:8000/redoc`

Default administrator credentials:
* **Email**: `admin@example.com`
* **Password**: `AdminSecurePassword123!`

---

## 3. Running with Docker Compose (Single Command)

To run the complete production stack (PostgreSQL 16 + FastAPI + Background ETL Worker + Redis):

```bash
docker compose up --build
```

To stop:
```bash
docker compose down
```

---

## 4. Single-Command Ingestion Execution

You can run individual files through the pipeline with a single CLI command:

```bash
# Ingest Retail CSV
python -m app.cli run-pipeline --source sample_data/retail/retail_sales.csv --domain retail --source-type csv

# Ingest Retail Excel (.xlsx)
python -m app.cli run-pipeline --source sample_data/retail/orders.xlsx --domain retail --source-type excel

# Ingest Products JSON
python -m app.cli run-pipeline --source sample_data/retail/products.json --domain retail --source-type json

# Ingest Banking Transactions CSV
python -m app.cli run-pipeline --source sample_data/banking/transactions.csv --domain banking --source-type csv
```

---

## 5. Running the Test Suite

Run the full pytest suite with branch coverage:
```bash
python -m pytest --cov=app --cov-report=term-missing
```

---

## 6. Future Improvements & Roadmap

1. **Distributed Processing**: Integrate Apache PySpark or Polars for multi-gigabyte/terabyte file ingestion.
2. **Message Queue Integration**: Decouple ingestion triggers with Apache Kafka or RabbitMQ event streaming.
3. **Automated Schema Evolution**: Support dynamic JSON schema drift and automated column migrations.
4. **Data Versioning**: Integrate Delta Lake or Apache Iceberg for table time-travel.
5. **Advanced Machine Learning**: Integrate churn prediction and transaction anomaly detection pipelines.
