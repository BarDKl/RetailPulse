# RetailPulse: Predictive Inventory API

**RetailPulse** is a backend microservice designed for e-commerce analytics. It ingests large-scale transactional data, performs customer segmentation, and forecasts metrics by utilizing Machine Learning models.

> **Goal:** To showcase a production-ready Machine Learning pipeline.

---

## Tech Stack

* **Language:** Python 3.12
* **Data Processing:** Polars, NumPy, Scikit-Learn
* **Frameworks:** FastAPI
* **Infrastructure:** Docker, Docker Compose, WSL2 (Ubuntu)
* **Database:** PostgreSQL 15 (Containerized)
* **IDE:** PyCharm Community

---

## Dataset
This project uses the **"Online Retail"** dataset from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/online+retail). It contains transactional data for a UK-based online retailer.

---

## Model Logic
In the current state, there are two models in the app. They both run on RFM data simultaneously.

### 1. Customer Segmentation
* **Algorithm:** K-Means Clustering.
* **Logic:** Groups customers into segments ("Casual", "Loyal", "VIP") based on RFM (Recency, Frequency, Monetary) analysis.
* **Goal:** To provide targeted marketing actions.

### 2. Customer Lifetime Value (CLV) Prediction
* **Algorithm:** Random Forest Regressor.
* **Logic:** Predicts the specific future dollar amount a customer is expected to spend.
* **Goal:** To prioritize high-value customers.

---

## 🔌 Example Usage

**Request:**
```json
{
  "recency": 325,
  "frequency": 1,
  "monetary": 77183.6,
  "customer_id": 12346
}
```
**Response:**
```json
{
  "customer_id": 12346,
  "segment": "VIP",
  "predicted_future_spend": "45916.19£"
}
```

## Startup
Execute this code in the terminal to open the app locally:
```shell
pip install -r requirements.txt
uvicorn app.main:app --reload
```
If you want to open it using docker execute this:
```shell
docker-compose build
docker-compose up
```
## Additional Info
* Pre-trained Models: The .pkl model files are included in the repo, so the API works out-of-the-box without training.

* Training Notebooks: If you want to view or run the notebooks for model training, you will need to download the dataset and install extra visualization packages:

```shell
pip install plotly polars matplotlib
```
