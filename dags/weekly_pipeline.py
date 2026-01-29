from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from app.ETL import ingest_clean
from app.final_models.segment_model import rfm_predictions
from app.final_models.clv_model import clv_predictions
from app.services import ModelService, write_to_postgres