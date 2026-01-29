import polars as pl
import numpy as np
from sqlalchemy import create_engine
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
import pickle
database_url = "postgresql://user:password@localhost:5432/retail_db"
engine = create_engine(database_url)
rfm_data = pl.read_database("""SELECT *FROM rfm_data""", connection = engine)

X = rfm_data.select(pl.exclude('customerid')).to_numpy()
full_pipeline = Pipeline([
    ('log', FunctionTransformer(np.log1p, validate=True)),
    ('scaler', StandardScaler()),
    ('kmeans', KMeans(n_clusters=3, random_state=42))
])
full_pipeline.fit(X)
labels = full_pipeline.predict(X)

filepath = "app/final_models/pickles/rfm_model.pkl"
with open(filepath, "wb") as f:
    pickle.dump(full_pipeline, f)
segment_map = {0 : 'Casual', 1: 'Loyal', 2: 'VIP'}
segments = [segment_map[i] for i in labels]
segments_to_save = rfm_data.select(pl.col('customerid')).with_columns(pl.Series(name = 'Segment', values = segments))
with engine.begin() as connection:
    segments_to_save.write_database(
        table_name="customers_segmented",
        connection=connection,
        if_table_exists="replace"
    )