from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.exceptions import AirflowSkipException
from datetime import datetime
import pathlib
import polars as pl
from app.ETL import ingest_clean, transform_to_rfm
from app.services import engine, ModelService, write_to_postgres
import pathlib

def ingest_csv_to_db(**kwargs):
    ds = kwargs['ds']
    path = pathlib.Path(f"/opt/airflow/data/future/{ds}.csv")

    if not path.exists():
        raise AirflowSkipException(f'No data for {ds}')
    ingest_clean(path,engine)

def transform_rfm():
    transform_to_rfm(engine)

def daily_predict_segment():
    df_rfm = pl.read_database("SELECT * FROM rfm_data", engine)
    service = ModelService()

    segment_labels = service.batch_predict_segment(df_rfm)

    results = df_rfm.select(pl.col('customerid')).with_columns(segment_labels)
    results.write_csv("/tmp/segment_preds.csv")

def daily_predict_clv():
    df_rfm = pl.read_database("SELECT * FROM rfm_data", engine)
    service = ModelService()

    clv_preds = service.batch_predict_clv(df_rfm)

    results = df_rfm.select(pl.col('customerid')).with_columns(clv_preds)
    results.write_csv("/tmp/clv_preds.csv")

def write_to_postgres_logic():
    rfm_res = pl.read_csv("/tmp/segment_preds.csv")
    clv_res = pl.read_csv("/tmp/clv_preds.csv")

    # Join the parallel results
    final_df = rfm_res.join(clv_res, on="customerid", how="inner")
    # Final write to DB
    write_to_postgres(final_df, table_name="customer_insights", engine=engine)


with DAG("daily_predictions", start_date=datetime(2011, 11, 9), schedule='@daily', catchup=False) as dag:
    ingest = PythonOperator(
        task_id="ingest_csv_to_db",
        python_callable=ingest_csv_to_db
    )

    transform = PythonOperator(
        task_id="transform_rfm_features",
        python_callable=transform_rfm
    )

    predict_rfm = PythonOperator(
        task_id="predict_segments",
        python_callable=daily_predict_segment
    )

    predict_clv = PythonOperator(
        task_id="predict_clv",
        python_callable=daily_predict_clv
    )

    write_results = PythonOperator(
        task_id="write_to_final_table",
        python_callable=write_to_postgres_logic
    )

    ingest >> transform >> [predict_rfm, predict_clv] >> write_results
