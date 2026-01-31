from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.exceptions import AirflowSkipException
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime
import pathlib
import polars as pl

# ETL & Services imports
from app.ETL import ingest_clean, transform_to_rfm
from app.services import engine, ModelService, write_to_postgres

# Training Imports
from app.final_models.segment_model import (
    train_segment,
    save_model as save_rfm_model,
    load_prepare_rfm_data
)
from app.final_models.clv_model import (
    train_clv,
    save_model as save_clv_model,
    load_prepare_clv_data
)

# --- CONFIG ---
SEGMENT_MODEL_PATH = pathlib.Path("/opt/airflow/plugins/app/final_models/pickles/segment_model.pkl")
CLV_MODEL_PATH = pathlib.Path("/opt/airflow/plugins/app/final_models/pickles/clv_model.pkl")


def ingest_csv_to_db(**kwargs):
    ds = kwargs['ds']
    path = pathlib.Path(f"/opt/airflow/data/future/{ds}.csv")

    if not path.exists():
        print(f"No new data for {ds}. Skipping Ingest and Transform.")
        raise AirflowSkipException(f'No data for {ds}')

    print(f"Found data for {ds}. Ingesting...")
    ingest_clean(path, engine)


def transform_rfm_task():
    transform_to_rfm(engine)


def train_rfm_logic():
    df = load_prepare_rfm_data(engine)

    pipeline = train_segment(df)
    save_rfm_model(pipeline, SEGMENT_MODEL_PATH)

def train_clv_logic():
    df = load_prepare_clv_data(engine)

    pipeline = train_clv(df)
    save_clv_model(pipeline, CLV_MODEL_PATH)

def weekly_predict_segment():
    service = ModelService()
    df_rfm = pl.read_database("SELECT * FROM rfm_data", engine)
    segment_labels = service.batch_predict_segment(df_rfm)
    results = df_rfm.select(pl.col('customerid')).with_columns(segment_labels)
    results.write_csv("/tmp/weekly_segment_preds.csv")

def weekly_predict_clv():
    service = ModelService()
    df_rfm = pl.read_database("SELECT * FROM rfm_data", engine)
    clv_preds = service.batch_predict_clv(df_rfm)
    results = df_rfm.select(pl.col('customerid')).with_columns(clv_preds)
    results.write_csv("/tmp/weekly_clv_preds.csv")

def write_to_postgres_weekly():
    rfm_res = pl.read_csv("/tmp/weekly_segment_preds.csv")
    clv_res = pl.read_csv("/tmp/weekly_clv_preds.csv")
    final_df = rfm_res.join(clv_res, on="customerid", how="inner")
    write_to_postgres(final_df, table_name="customer_insights", engine=engine, keyword = 'replace')


with DAG(
        "weekly_retraining_and_prediction",
        start_date=datetime(2011, 11, 9),
        schedule='@weekly',
        catchup=False
) as dag:
    ingest = PythonOperator(
        task_id="ingest_weekly_data",
        python_callable=ingest_csv_to_db
    )

    transform = PythonOperator(
        task_id="update_rfm_features",
        python_callable=transform_rfm_task
    )

    train_rfm_model = PythonOperator(
        task_id="retrain_rfm_model",
        python_callable=train_rfm_logic,
        trigger_rule=TriggerRule.NONE_FAILED
    )

    train_clv_model = PythonOperator(
        task_id="retrain_clv_model",
        python_callable=train_clv_logic,
        trigger_rule=TriggerRule.NONE_FAILED
    )

    predict_rfm = PythonOperator(
        task_id="predict_segments_new_model",
        python_callable=weekly_predict_segment,
        trigger_rule = TriggerRule.NONE_FAILED
    )

    predict_clv = PythonOperator(
        task_id="predict_clv_new_model",
        python_callable=weekly_predict_clv,
        trigger_rule=TriggerRule.NONE_FAILED
    )

    write_results = PythonOperator(
        task_id="write_results_to_db",
        python_callable=write_to_postgres_weekly,
        trigger_rule=TriggerRule.NONE_FAILED
    )


    ingest >> transform

    transform >> [train_rfm_model, train_clv_model]

    train_rfm_model >> predict_rfm
    train_clv_model >> predict_clv

    [predict_rfm, predict_clv] >> write_results