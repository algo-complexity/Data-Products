from typing import Optional
from requests import get
from datetime import datetime
import pandas as pd
from config import Config, config

config: Config

base_url = "https://yh-finance.p.rapidapi.com"
headers = {
    "X-RapidAPI-Key": config.yahoo_finance_header_key,
    "X-RapidAPI-Host": "yh-finance.p.rapidapi.com",
}


def get_yahoo_autocomplete_stock_ticker(search: str) -> Optional[str]:
    response = get(f"{base_url}/auto-complete", headers=headers, params={"q": search})
    quotes = response.json()["quotes"]
    if quotes == []:
        return None
    return quotes[0]["symbol"]


def get_yahoo_stock_metadata(ticker: str) -> dict:
    response = get(
        f"{base_url}/stock/v2/get-summary", headers=headers, params={"symbol": ticker}
    )
    json = response.json()
    print("fetch stock data")
    data = {
        "stock": {
            "name": json["quoteType"]["shortName"],
            "ticker": json["symbol"],
            "summary": json["summaryProfile"]["longBusinessSummary"],
        },
        "exchange": {"short_name": json["quoteType"]["exchange"]},
    }
    return data


def get_yahoo_stock_price(ticker: str) -> Optional[pd.DataFrame]:
    """Gets the stock prices for a given stock

    Args:
        ticker (str): The ticker symbol for a stock

    Returns:
        pandas DataFrame
    """
    querystring = {
        "interval": "1d",
        "symbol": ticker,
        "range": "1mo",
        "includeAdjustedClose": "true",
    }

    response = get(
        f"{base_url}/stock/v3/get-chart", headers=headers, params=querystring
    ).json()
    if response["chart"]["error"]:
        return

    result = response["chart"]["result"][0]

    data = {
        "timestamp": result["timestamp"],
        "high": result["indicators"]["quote"][0]["high"],
        "low": result["indicators"]["quote"][0]["low"],
        "open": result["indicators"]["quote"][0]["open"],
        "close": result["indicators"]["quote"][0]["close"],
    }
    df = pd.DataFrame(data=data)
    df["timestamp"] = df["timestamp"].apply(datetime.fromtimestamp)
    return df
