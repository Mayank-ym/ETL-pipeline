import pandas as pd
import json
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path


def expand_prefix(col):
    col = re.sub(r"^ath", 'all_time_high', col)
    col = re.sub(r"^atl", "all_time_low", col)
    return col

def convert_to_date(df):
    date_cols = [cols for cols in df.columns if "date" in cols.lower()]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col]).dt.date
    return df

def roi_breakdown(df):

    for key in ["times", "currency", "percentage"]:
        df["roi_" + key] = None

    for i in range(len(df)):
        value = df.loc[i, "roi"]
        if value:
            df.loc[i, "roi_times"] = value["times"]
            df.loc[i, "roi_currency"] = value["currency"]
            df.loc[i, "roi_percentage"] = value["percentage"]
    return df

def run_etl():
    # extraction
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
    response = requests.get(url)
    # print(response)

    data = response.json()
    # print(data[0])


    #Transformation
    df = pd.DataFrame(data)

    # drop image column
    df = df.drop(columns=['image'])


    # column renaming
    df = df.rename(columns = expand_prefix)

    df = df.rename(columns={
                            'id': 'GekoCoin_id', 
                            "current_price": "current_price_USD", 
                            "market_cap": "market_cap_USD", 
                            "high_24h": "highest_in_24h_USD", 
                            "low_24h": "lowest_in_24h_USD", 
                            "price_change_24h": "price_change_24h_USD", 
                            "fully_diluted_valuation": "fully_diluted_valuation_USD",
                            "all_time_high": "all_time_high_USD",
                            "all_time_low": "all_time_low_USD"
    })


    #type conversion
    # print(df.info())

    df = convert_to_date(df)
    # print(df.info())
    # print(df.head())

    df["ETL_fetched_at"] = pd.Timestamp.now().floor("s")

    # print(df)

    df = roi_breakdown(df)

    # round every float column to 2 decimal places
    df[["roi_times", "roi_percentage"]] = df[["roi_times", "roi_percentage"]].apply(pd.to_numeric)
    df = df.round(2)
    # print(df.head())

    # df.to_csv(Path(__file__).resolve().parents[1] / "data" / "Crypto_data.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M")
    df.to_csv(f"/opt/airflow/data/Crypto_data_{stamp}.csv", index=False)

    # print(Path(__file__).parents[1])