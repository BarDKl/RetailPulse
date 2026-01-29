import polars as pl
import numpy as np
import sklearn
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
import pickle

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

