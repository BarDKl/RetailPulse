from sqlalchemy import create_engine
import pathlib
import polars as pl

csv_path = pathlib.Path('~/PycharmProjects/retail.pred_api/data/retail_data.csv')

database_url = "postgresql://user:password@localhost:5432/retail_db"
# First preparations of the data
df = pl.read_csv(csv_path,
                 schema_overrides={"InvoiceNo": pl.String},
                 try_parse_dates=True)
df.columns = [name.lower() for name in df.columns]
# Removing the discounts/returns (negative quantities) for math reliability and simplicity
df = df.filter(~(pl.col('invoiceno').str.starts_with(('A')))&~(pl.col('invoiceno').str.starts_with(('C'))))
df = df.select(pl.col('invoiceno').cast(pl.Int32),
    pl.exclude('invoiceno'))

# Writing the database
engine = create_engine(database_url)
df.write_database('retail_db', connection = engine)