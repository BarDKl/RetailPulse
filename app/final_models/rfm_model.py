import polars as pl
import numpy as np
from sqlalchemy import create_engine
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
import pickle
database_url = "postgresql://user:password@localhost:5432/retail_db"
connection = create_engine(database_url)
retail_data = pl.read_database(
    """with cte(maxdate) as(select max(invoicedate) from retail_db)
       select
           customerid,
           count(distinct invoiceno) as frequency,
           extract(day from (maxdate-max(invoicedate))) as recency,
           sum(quantity*unitprice) as monetary
       from retail_db, cte
       where customerid is not null
       group by customerid, maxdate"""
    ,connection = connection)

X = retail_data.select(pl.exclude('customerid')).to_numpy()
full_pipeline = Pipeline([
    ('log', FunctionTransformer(np.log1p, validate=True)),
    ('scaler', StandardScaler()),
    ('kmeans', KMeans(n_clusters=3, random_state=42))
])
full_pipeline.fit(X)
labels = full_pipeline.predict(X)

segments_to_save = retail_data.with_columns(
    pl.Series(name = 'cluster', values = labels)
)

filepath = "app/final_models/pickles/rfm_model.pkl"
with open(filepath, "wb") as f:
    pickle.dump(full_pipeline, f)


segments_to_save.write_database(
    table_name="customers_segmented",
    connection=connection, # Using the connection you created earlier
    if_table_exists="replace"
)
