import polars as pl
import numpy as np
from sklearn.metrics import mean_absolute_error
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import pathlib
import pickle

database_url = "postgresql://user:password@localhost:5432/retail_db"
engine = create_engine(database_url)
# to do this first we have to find the cutoff date which splits the time of our data in 70/30
q_cutoff = """
WITH date_range AS (
    SELECT MIN(invoicedate) as min_date, MAX(invoicedate) as max_date
    FROM transactions
),
duration AS (
    SELECT max_date - min_date as total_days FROM date_range
)
SELECT
    min_date + (total_days * 0.7) as cutoff_date
FROM date_range, duration
"""
cutoff_date = pl.read_database(q_cutoff, engine)[0,0]

rfm_data = pl.read_database(f"""
    SELECT
        customerid,
        COUNT(invoiceno) as frequency,
        EXTRACT(DAY FROM (DATE '{cutoff_date}' - MAX(invoicedate))) as recency,
        SUM(quantity * unitprice) as monetary
    FROM retail_db
    WHERE customerid IS NOT NULL AND invoicedate <= '{cutoff_date}'
    GROUP BY customerid
""", engine)
target_data = pl.read_database(f"""
    SELECT
        customerid,
        SUM(quantity * unitprice) as target_monetary
    FROM retail_db
    WHERE customerid IS NOT NULL AND invoicedate > '{cutoff_date}'
    GROUP BY customerid
""", engine)

final_data = rfm_data.join(target_data, on='customerid', how='left').filter((pl.col('target_monetary')<40000)&(pl.col('monetary')<40000)).fill_null(0)

X = final_data.select(pl.col('recency'),pl.col('frequency'),pl.col('monetary')).to_numpy()
Y = final_data.get_column('target_monetary').to_numpy()

final_model = RandomForestRegressor(n_estimators=200, max_depth=5, random_state=42)
final_model.fit(X, Y)

save_path = "app/final_models/pickles/clv_model.pkl"
pathlib.Path(save_path).parent.mkdir(parents=True, exist_ok=True)
with open(save_path, "wb") as f:
    pickle.dump(final_model, f)
