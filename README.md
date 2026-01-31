# 🚀 RetailPulse: Predictive Inventory API & ETL

![Status](https://img.shields.io/badge/status-active_development-brightgreen)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![Docker](https://img.shields.io/badge/docker-compose-2496ED)
![Airflow](https://img.shields.io/badge/apache_airflow-017CEE)
![FastAPI](https://img.shields.io/badge/FastAPI-005571)

**RetailPulse** is an enterprise-grade analytics platform designed to modernize retail operations. It bridges the gap between raw transactional data and actionable business insights by orchestrating a robust **ETL pipeline** with **Machine Learning** capabilities.

---

## 🏗 System Architecture

RetailPulse operates as a microservices architecture orchestrated via Docker:

### 1. 🧠 Predictive API (Microservice)
*   **Tech Stack**: FastAPI, Scikit-Learn.
*   **Role**: Serves real-time customer insights.
*   **Capabilities**:
    *   **Customer Segmentation**: Uses K-Means clustering to categorize users (e.g., "VIP", "Churn Risk").
    *   **CLV Prediction**: Uses Random Forest Regression to forecast Customer Lifetime Value.

### 2. 🔄 Automated ETL Pipeline (Orchestrator)
*   **Tech Stack**: Apache Airflow, Polars.
*   **Role**: Manages the data lifecycle from ingestion to inference.
*   **Workflows (DAGs)**:
    *   `daily_pipeline`: Ingests new transaction data from `data/future/`, cleans it, and updates predictions.
    *   `initial_pipeline`: bootstraps the system with historical data.

### 3. 🗄️ Data Storage
*   **PostgreSQL**: Dual-database setup.
    *   **Retail DB**: Stores processed RFM metrics and ML predictions.
    *   **Airflow DB**: Manages DAG metadata and scheduling.

---

## 🛠 Prerequisites

Before starting, ensure you have the following installed:
*   **Docker Desktop** (or Engine + Compose)
*   **Python 3.12+** (for local scripts)
*   **Git**

---

## 🚀 Quick Start Guide

Follow these steps to get RetailPulse running on your local machine.

### 1. Environment Setup & Data
The project includes a helper script to fetch the UCI Online Retail dataset and split it into "past" (training) and "future" (simulation) data.

**Requirements for Data Script:**
The data download script requires `pandas` and `ucimlrepo`. Install them locally:
```bash
pip install pandas ucimlrepo polars
```

**Run the Data Loader:**
```bash
python scripts/download_split_data.py
```
*This will create a `data/` directory with `retail_data.csv`, `past.csv` and a `future/` folder containing daily transaction files.*

### 2. Launch the Application
Start the entire stack using the helper script:
```bash
./scripts/start_app.sh
```
*This script runs `docker-compose up -d --build`, spinning up Airflow (Webserver, Scheduler, Triggerer), Postgres, and the FastAPI app.*

### 3. Access Interfaces
Once everything is running, open the dashboards:
```bash
./scripts/open_ui.sh
```
Or access them manually:
*   **Airflow UI**: [http://localhost:8080](http://localhost:8080) *(User/Pass: `airflow`/`airflow`)*
*   **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🕹️ Managing the Application

We provide a suite of scripts in the `scripts/` directory to simplify management:

| Script | Description |
| :--- | :--- |
| `./scripts/start_app.sh` | **Builds** and **Starts** all containers in detached mode. |
| `./scripts/stop_app.sh` | **Stops** and removes containers (preserves volumes). |
| `./scripts/open_ui.sh` | Opens the Airflow UI and API Docs in your default browser. |
| `python scripts/download_split_data.py` | Downloads and prepares the demo dataset. |

---

## 🔌 API Usage Example

Interact with the API to get predictions for a specific customer profile.

**Endpoint**: `POST /predict`

**Request**:
```json
{
  "recency": 12,
  "frequency": 5,
  "monetary": 1250.50,
  "customer_id": 9999
}
```

**Response**:
```json
{
  "customer_id": 9999,
  "segment": "Loyal",
  "predicted_future_spend": "1400.20£"
}
```

---

## 📂 Project Structure

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

---

<div align="center">
  <sub>Built with ❤️ by Barto</sub>
</div>
