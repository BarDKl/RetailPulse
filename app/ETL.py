import polars as pl

# Extraction and first cleans
def ingest_clean(path,engine):
    """
    This Function ingests transaction data from csv, cleans it and writes it into the database
    """
    df = pl.read_csv(path, try_parse_dates=True, schema_overrides={"invoiceno": pl.String, 'stockcode': pl.String})
    df.columns = [name.lower() for name in df.columns]
    df = df.filter(
        ~(pl.col('invoiceno').str.contains(('A'))) &
        ~(pl.col('invoiceno').str.contains(('C'))) &
        (pl.col('quantity') > 0)&(pl.col('unitprice') > 0)
    )
    df = df.select(pl.col('invoiceno').cast(pl.Int32), pl.exclude('invoiceno'))
    df.write_database('transactions', connection=engine, if_table_exists='append')
    return df

#Transformations
def transform_to_rfm(engine):
    """
    This Function transforms transaction data into rfm data
    """
    df = pl.read_database("""with cte(maxdate) as(select max(invoicedate) from transactions)
       select
           customerid,
           extract(day from (maxdate-max(invoicedate))) as recency,
           round(count(distinct invoiceno),2) as frequency,
           round(sum(cast(quantity as numeric)*cast(unitprice as numeric)),2)as monetary
       from transactions, cte
       where customerid is not null
       group by customerid, maxdate""", connection = engine)
    df.write_database('rfm_data', connection=engine, if_table_exists='append')

