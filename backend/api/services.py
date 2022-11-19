from typing import Optional

import numpy as np
import pandas as pd
import praw
from django.db.models import QuerySet
from django.utils.timezone import datetime, utc
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from requests import get
from serpapi import GoogleSearch
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.volatility import AverageTrueRange

from dataprod.config import Config, config

from . import models

config: Config

reddit = praw.Reddit(
    client_id=config.reddit_client_id,
    client_secret=config.reddit_client_secret,
    user_agent=config.reddit_user_agent,
)


base_url = "https://yh-finance.p.rapidapi.com"
headers = {
    "X-RapidAPI-Key": config.yahoo_finance_header_key,
    "X-RapidAPI-Host": "yh-finance.p.rapidapi.com",
}


def calculate_indices(stock: models.Stock):
    prices = (
        stock.price_set.all().order_by("timestamp").values_list("high", "low", "close")
    )
    prices_df = pd.DataFrame(prices, columns=["high", "low", "close"])

    # Initialise all the indicators
    sma_50 = SMAIndicator(close=prices_df["close"], window=50)
    sma_100 = SMAIndicator(close=prices_df["close"], window=100)
    sma_200 = SMAIndicator(close=prices_df["close"], window=200)
    ema_50 = EMAIndicator(close=prices_df["close"], window=50)
    ema_100 = EMAIndicator(close=prices_df["close"], window=100)
    ema_200 = EMAIndicator(close=prices_df["close"], window=200)
    macd = MACD(close=prices_df["close"])
    rsi = RSIIndicator(close=prices_df["close"])
    atr = AverageTrueRange(
        high=prices_df["high"], low=prices_df["low"], close=prices_df["close"]
    )

    models.Indicator.objects.update_or_create(
        stock=stock, name="sma_50", defaults=dict(value=sma_50.sma_indicator().iloc[-1])
    )
    models.Indicator.objects.update_or_create(
        stock=stock,
        name="sma_100",
        defaults=dict(value=sma_100.sma_indicator().iloc[-1]),
    )
    models.Indicator.objects.update_or_create(
        stock=stock,
        name="sma_200",
        defaults=dict(value=sma_200.sma_indicator().iloc[-1]),
    )
    models.Indicator.objects.update_or_create(
        stock=stock, name="ema_50", defaults=dict(value=ema_50.ema_indicator().iloc[-1])
    )
    models.Indicator.objects.update_or_create(
        stock=stock,
        name="ema_100",
        defaults=dict(value=ema_100.ema_indicator().iloc[-1]),
    )
    models.Indicator.objects.update_or_create(
        stock=stock,
        name="ema_200",
        defaults=dict(value=ema_200.ema_indicator().iloc[-1]),
    )
    models.Indicator.objects.update_or_create(
        stock=stock, name="macd", defaults=dict(value=macd.macd_diff().iloc[-1])
    )
    models.Indicator.objects.update_or_create(
        stock=stock, name="rsi", defaults=dict(value=rsi.rsi().iloc[-1])
    )
    models.Indicator.objects.update_or_create(
        stock=stock, name="atr", defaults=dict(value=atr.average_true_range().iloc[-1])
    )


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
        "range": "2y",
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
            stock, _ = models.Stock.objects.update_or_create(
                ticker=data["ticker"],
                defaults=dict(name=data["name"], summary=data["summary"]),
            )

            if stock:
                stock_data = get_yahoo_stock_price(ticker)
                for _, _open, high, low, close, timestamp in stock_data.itertuples():
                    models.Price.objects.update_or_create(
                        timestamp=timestamp,
                        stock=stock,
                        defaults=dict(open=_open, high=high, low=low, close=close),
                    )
                calculate_indices(stock)
            stock = models.Stock.objects.filter(ticker=ticker)
    return stock


def get_reddit_posts(subreddit, symb, time="week") -> pd.DataFrame:
    """Fetches reddit posts and relevant information sentiment score.

    Args:
        subreddit (str): name of subreddit eg. "wallstreetbets"
        symb (str): symbol to search for eg. "BBBY"
        time (str, optional): Time period for fetching posts. Defaults to "week".

    Returns:
        DataFrame: Pandas df
    """
    posts = []
    sent = SentimentIntensityAnalyzer()
    for post in reddit.subreddit(subreddit).search(symb, time_filter=time):
        if post.is_self:
            posts.append(
                [
                    post.title,
                    post.selftext,
                    datetime.fromtimestamp(post.created, tz=utc),
                    post.author.name,
                    round(sent.polarity_scores(post.selftext)["compound"], 2),
                    post.score,
                    post.num_comments,
                    post.url,
                    post.id,
                ]
            )
    df = pd.DataFrame(
        posts,
        columns=[
            "title",
            "content",
            "timestamp",
            "author",
            "sentiment",
            "score",
            "num_comments",
            "url",
            "api_id",
        ],
    )
    # remove rows with empty strings/null
    df.replace("", np.nan, inplace=True)
    df.dropna(inplace=True)
    return df


def get_image_url(query):
    params = {"q": query, "tbm": "isch", "ijn": "0", "api_key": config.google_api_key}

    search = GoogleSearch(params)
    results = search.get_dict()
    suggested = results["suggested_searches"]
    image_url = [result for result in suggested if result["name"] == "logo"]
    if image_url:
        return image_url[0]["thumbnail"]
    return "https://static.thenounproject.com/png/3674270-200.png"
