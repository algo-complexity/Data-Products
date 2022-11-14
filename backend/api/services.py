from . import models
from typing import Optional
import pandas as pd

from requests import get
from dataprod.config import Config, config

from django.utils.timezone import datetime, utc
from django.db.models import QuerySet

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


def get_yahoo_stock_data(ticker: str) -> dict:
    response = get(
        f"{base_url}/stock/v2/get-summary", headers=headers, params={"symbol": ticker}
    )
    json = response.json()
    data = {
        "name": json["quoteType"]["shortName"],
        "ticker": json["symbol"],
        "summary": json["summaryProfile"]["longBusinessSummary"],
    }
    return data


def get_yahoo_stock_price(ticker: str) -> pd.DataFrame:
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
        "open": result["indicators"]["quote"][0]["open"],
        "high": result["indicators"]["quote"][0]["high"],
        "low": result["indicators"]["quote"][0]["low"],
        "close": result["indicators"]["quote"][0]["close"],
        "timestamp": result["timestamp"],
    }
    df = pd.DataFrame(data=data)
    df["timestamp"] = df["timestamp"].apply(datetime.fromtimestamp, tz=utc)
    return df

def get_stock_from_yahoo(search: str) -> QuerySet:
    ticker = get_yahoo_autocomplete_stock_ticker(search)
    stock = models.Stock.objects.none()
    if ticker:
        stock = models.Stock.objects.filter(ticker=ticker)
        if not stock.exists():
            data = get_yahoo_stock_data(ticker)
            stock, _ = models.Stock.objects.update_or_create(ticker=data["ticker"], defaults=dict(name=data["name"], summary=data["summary"]))

            # TODO: Add Extra code to calculate indicators
            if stock:
                stock_data = get_yahoo_stock_price(ticker)
                for _, _open, high, low, close, timestamp in stock_data.itertuples():
                    models.Price.objects.update_or_create(timestamp=timestamp, stock=stock, defaults=dict(open=_open, high=high, low=low, close=close))
            stock = models.Stock.objects.filter(ticker=ticker)
    return stock