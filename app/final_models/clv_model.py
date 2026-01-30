import polars as pl
import sklearn.pipeline
from sklearn.ensemble import RandomForestRegressor
import pickle


# to do this first we have to find the cutoff date which splits the time of our data in 70/30
def load_prepare_clv_data(engine):
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
    return final_data

def train_clv(df_prepared: pl.DataFrame) -> sklearn.pipeline.Pipeline:
    X = df_prepared.select(pl.col('recency'), pl.col('frequency'), pl.col('monetary')).to_numpy()
    Y = df_prepared.get_column('target_monetary').to_numpy()
    pipeline = sklearn.pipeline.Pipeline([('RFR', RandomForestRegressor(n_estimators=200, max_depth=5, random_state=42))])
    pipeline.fit(X, Y)
    return pipeline


def save_model(pipeline, path) -> None:
    with open(path, "wb") as f:
        pickle.dump(pipeline, f)
