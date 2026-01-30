import polars as pl
import numpy as np
import sklearn
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
import pickle
import os
from sqlalchemy import create_engine
import pathlib

def load_prepare_rfm_data(engine) -> pl.DataFrame:
    df = pl.read_database("""SELECT * FROM rfm_data""", engine)
    return df

def train_rfm(rfm_data: pl.DataFrame) -> sklearn.pipeline.Pipeline:
    X = rfm_data.select(pl.exclude('customerid')).to_numpy()
    full_pipeline = Pipeline([
        ('log', FunctionTransformer(np.log1p, validate=True)),
        ('scaler', StandardScaler()),
        ('kmeans', KMeans(n_clusters=3, random_state=42))
    ])
    full_pipeline.fit(X)
    return full_pipeline

def save_model(pipeline: sklearn.pipeline.Pipeline, filepath) -> None:
    with open(filepath, "wb") as f:
        pickle.dump(pipeline, f)

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/retail_db"
)

engine = create_engine(DB_URL)
save_model(train_rfm(load_prepare_rfm_data(engine=engine)), pathlib.Path.joinpath(pathlib.Path('.').absolute(), 'app', 'final_models', 'pickles', 'segment_model.pkl'))
