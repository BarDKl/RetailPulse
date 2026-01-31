from pathlib import Path
import pathlib
from datetime import timedelta
import pandas as pd
import polars as pl
from ucimlrepo import fetch_ucirepo 

def fetch_data():
    print("Fetching data from UCI Machine Learning Repository...")
    retail_data = fetch_ucirepo(id=352).data.original
    
    # Resolve project root relative to this script
    project_root = pathlib.Path(__file__).parent.parent.absolute()
    data_dir = project_root / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    data_path = data_dir / 'retail_data.csv'
    retail_data.to_csv(data_path, index=False)
    print(f"Data downloaded to {data_path}")

def split_csv():
    """
    This function splits a csv file into two csv files simulating past and future data
    """
    print("Reading and processing data...")
    project_root = pathlib.Path(__file__).parent.parent.absolute()
    csv_path = project_root / 'data' / 'retail_data.csv'
    
    df = pl.read_csv(csv_path, try_parse_dates=True, schema_overrides={"InvoiceNo": pl.String}, ignore_errors=True)
    df.columns = [name.lower() for name in df.columns]
    
    # Ensure correct date parsing if auto-parse failed
    if df['invoicedate'].dtype == pl.String:
        try:
             df = df.with_columns(pl.col('invoicedate').str.strptime(pl.Datetime, "%m/%d/%Y %H:%M"))
        except:
             pass

    max_date = df.select(pl.max('invoicedate'))[0,0]
    cutoff_date = max_date - timedelta(days=30)
    
    df1 = df.filter(pl.col('invoicedate') <= cutoff_date)
    df2 = df.filter(pl.col('invoicedate') > cutoff_date)
    return df1, df2

def split_future(df: pl.DataFrame):
    """
    This Function splits 'future' data into individual days
    """
    results = {}
    if df.is_empty():
        return results
        
    # Get range of dates
    df_dates = df.with_columns(pl.col('invoicedate').dt.date().alias('date_only'))
    unique_dates = df_dates.select('date_only').unique().sort('date_only')['date_only']
    
    for date_val in unique_dates:
        name = date_val.strftime('%Y-%m-%d')
        dfp = df.filter(pl.col('invoicedate').dt.date() == date_val)
        if not dfp.is_empty():
            results[name] = dfp
            
    return results

def write_csvs(finalpath: Path, datasets: dict[str, pl.DataFrame]) -> None:
    """
    This Function writes csv files into a chosen directory
    """
    if not finalpath.is_dir():
        finalpath.mkdir(parents=True, exist_ok=True)
        
    for name, data in datasets.items():
        output_file = finalpath / f'{name}.csv'
        data.write_csv(output_file)

if __name__ == "__main__":
    project_root = pathlib.Path(__file__).parent.parent.absolute()
    data_path = project_root / 'data'
    future_path = data_path / 'future'
    
    fetch_data()
    past, future = split_csv()
    
    print("Splitting future data by day...")
    future_split = split_future(future)
    
    print("Writing files...")
    write_csvs(data_path, {'past': past})
    write_csvs(future_path, future_split)
    print("Done!")