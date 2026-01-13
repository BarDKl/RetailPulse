from sqlalchemy import create_engine
import pathlib
import polars as pl

csv_path = pathlib.Path('~/PycharmProjects/retail.pred_api/data/retail_data.csv')

database_url = "postgresql://user:password@localhost:5432/retail_db"

df = pl.read_csv(csv_path, schema_overrides={"InvoiceNo": pl.String})

engine = create_engine(database_url)

df.write_database('retail_db', connection = engine)