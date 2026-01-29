from pathlib import Path
import polars as pl
import pathlib
from datetime import timedelta

def split_csv():
    """
    This function splits a csv file into two csv files simulating past and future data
    """
    csv_path = pathlib.Path.joinpath(pathlib.Path('__file__').parent.absolute(), 'data', 'retail_data.csv')
    df = pl.read_csv(csv_path, try_parse_dates=True, schema_overrides={"InvoiceNo": pl.String})
    df.columns = [name.lower() for name in df.columns]
    df1 = df.filter(pl.col('invoicedate') <= (pl.max('invoicedate') - timedelta(days = 30)))
    df2 = df.filter(pl.col('invoicedate') > (pl.max('invoicedate') - timedelta(days = 30)))
    return df1, df2

def split_future(df: pl.DataFrame):
    """
    This Function splits 'future' data into individual days
    """
    results = {}
    mindate = df.select(pl.min('invoicedate'))[0,0]
    maxdate = df.select(pl.max('invoicedate'))[0,0]
    while mindate <= maxdate:
        name = f"{mindate.strftime('%Y-%m-%d')}"
        dfp = df.filter(pl.col('invoicedate') == mindate)
        if not dfp.is_empty():
            results[name] = dfp
        mindate = mindate + timedelta(days=1)
    return results

def write_csvs(finalpath: Path,datasets: dict[str : pl.DataFrame]) -> None:
    """
    This Function writes csv files into a chosen directory
    """
    if not finalpath.is_dir():
        finalpath.mkdir(parents=True)
    for i in datasets:
        with pathlib.Path.joinpath(finalpath, f'{i}.csv').open('w') as f:
            datasets[i].write_csv(f)


data_path = pathlib.Path.joinpath(pathlib.Path('__file__').parent.absolute(), 'data')
future_path = pathlib.Path.joinpath(data_path, 'future')

past, future = split_csv()
future_split = split_future(future)
write_csvs(data_path, {'past':past})
write_csvs(future_path,future_split)