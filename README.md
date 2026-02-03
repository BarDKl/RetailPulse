# RetailPulse: Predictive Inventory API & ETL

![Status](https://img.shields.io/badge/status-active_development-brightgreen)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![Docker](https://img.shields.io/badge/docker-compose-2496ED)
![Airflow](https://img.shields.io/badge/apache_airflow-017CEE)
![FastAPI](https://img.shields.io/badge/FastAPI-005571)

**RetailPulse** is an  analytics platform designed to modernize retail operations. It bridges the gap between raw transactional data and actionable business insights by orchestrating a robust **Machine Learning** pipeline.

---

## System Architecture

RetailPulse operates as a microservices architecture orchestrated via Docker:

### 1. Predictive API (Microservice)
*   **Tech Stack**: FastAPI, Scikit-Learn.
*   **Role**: Serves real-time customer insights.
*   **Capabilities**:
    *   **Customer Segmentation**: Uses K-Means clustering to categorize users (eg. "Casual","VIP").
    *   **CLV Prediction**: Uses Random Forest Regression to forecast Customer Lifetime Value.

### 2. Automated ETL Pipeline (Orchestrator)
*   **Tech Stack**: Apache Airflow, Polars.
*   **Role**: Manages the data lifecycle from ingestion to inference.
*   **Workflows (DAGs)**:
    *   `initial_training_and_prediction`: Bootstraps the system (historical data).
    *   `daily_predictions`: Runs daily ETL and inference.
    *   `weekly_retraining_and_prediction`: Retrains models weekly.

### 3. Data Storage
*   **PostgreSQL**: Dual-database setup (Retail DB & Airflow DB).

---

## Prerequisites

Ensure you have the following installed:

```bash
# Verify Docker is installed
docker --version

# Verify Docker Compose is installed
docker-compose --version

# Verify Python is installed (3.12+ recommended)
python --version
```

---

## Quick Start Guide

### 1. Environment Setup & Data

Install the required Python dependencies for the data loader:

```bash
pip install pandas ucimlrepo polars
```

Download and prepare the dataset (splits into `past.csv` and `future/` daily files):

```bash
python scripts/download_split_data.py
```

### 2. Launch the Application

Build and start the entire stack (Airflow, Postgres, FastAPI) in detached mode:

```bash
docker-compose up -d --build
```

### 3. Access Interfaces

*   **Airflow UI**: [http://localhost:8080](http://localhost:8080)
    *   User: `airflow`
    *   Pass: `airflow`
*   **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Managing the Application

Common commands for managing the application lifecycle:

**Start the Application:**
```bash
docker-compose up -d
```

**Stop the Application:**
```bash
docker-compose down
```

**View Application Logs:**
```bash
docker-compose logs -f
```

**Rebuild Containers (after code changes):**
```bash
docker-compose up -d --build
```

**Reset Data (WARNING: Deletes all DB volumes):**
```bash
docker-compose down -v
```

---

## API Usage Example

Interact with the API to get predictions for a specific customer profile.

**Endpoint**: `POST /predict`

**Request:**

```json
{
  "recency": 12,
  "frequency": 5,
  "monetary": 1250.50,
  "customer_id": 9999
}
```

**Response:**

```json
{
  "customer_id": 9999,
  "segment": "Loyal",
  "predicted_future_spend": "1400.20£"
}
```

---

## Project Structure

```text
retail.pred_api/
├── app/                  # FastAPI Application & ML Models
├── dags/                 # Airflow DAGs (ETL & Retraining)
├── data/                 # Dataset Storage (GitIgnored)
│   ├── future/           # Daily CSVs for simulation
│   └── past.csv          # Historical training data
├── scripts/              # Helper shell/python scripts
└── docker-compose.yaml   # Container orchestration
```
