import pathlib as pth
import pickle
import numpy as np
import polars as pl
import os
from sqlalchemy import create_engine


DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/retail_db"
)

engine = create_engine(DB_URL)


class ModelService:
    def __init__(self):
        self.models_dir = pth.Path('/opt/airflow/app/final_models/pickles')
        self.segment_path = self.models_dir / 'segment_model.pkl'
        self.clv_path = self.models_dir / 'clv_model.pkl'
        self.rfm_model = None
        self.clv_model = None
        self.load_models()

    def load_models(self):
        try:
            if pth.Path.exists(self.rfm_path):
                with open(self.rfm_path, 'rb') as f:
                    self.rfm_model = pickle.load(f)
                print('RFM Model loaded successfully')
            else:
                print(f"ERROR: RFM model not found at {self.rfm_path}")
        except Exception as e:
            print(f"ERROR loading RFM model: {e}")
        try:
            if pth.Path.exists(self.clv_path):
                with open(self.clv_path, "rb") as f:
                    self.clv_model = pickle.load(f)
                print("CLV Model loaded successfully")
            else:
                print(f"Warning: CLV model not found at {self.clv_path}")
        except Exception as e:
            print(f"Error loading CLV model: {e}")

    def predict_segment(self, recency, frequency, monetary):
        if not self.rfm_model:
            raise 'no model loaded'
        input_data = np.array([[recency, frequency, monetary]])
        prediction = self.rfm_model.predict(input_data)[0]
        segment_map = {0: 'Casual', 1: 'Loyal', 2: 'VIP'}
        return segment_map.get(int(prediction), 'Unknown')

    def batch_predict_segment(self, df: pl.DataFrame) -> pl.Series:
        if not self.rfm_model:
            raise 'no model loaded'
        X = df.select(['recency', 'frequency', 'monetary']).to_numpy()
        preds = self.rfm_model.predict(X)
        segment_map = {0: 'Casual', 1: 'Loyal', 2: 'VIP'}
        return pl.Series(name = "segment", values = [segment_map[i] for i in preds])

    def predict_clv(self, recency, frequency, monetary):
        if not self.clv_model:
            raise 'no model loaded'
        input_data = np.array([[recency, frequency, monetary]])
        prediction = self.clv_model.predict(input_data)[0]
        return round(prediction,2)
    def batch_predict_clv(self, df: pl.DataFrame) -> pl.Series:
        if not self.clv_model:
            raise 'no model loaded'
        X = df.select(['recency', 'frequency', 'monetary']).to_numpy()
        predictions = self.clv_model.predict(X)
        return pl.Series(name = "predicted_spend", values = predictions)

def write_to_postgres(df: pl.DataFrame, table_name: str, engine):
    with engine.begin() as conn:
        df.write_database(
            table_name=table_name,
            connection=conn,
            if_table_exists="append"
        )

run_model = ModelService()

# Daily Pipeline
#
# ingest_clean -> transform_to_rfm -> predict_rfm + predict_clv -> write_to_db
#
# Weekly Pipeline
#
# ingest_clean ->transform_to_rfm + transform_to_clv -> train_rfm + train_clv -> predict_rfm + predict_clv -> write_to_db
