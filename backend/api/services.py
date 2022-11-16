from . import models
from typing import Optional
import pandas as pd
import re

from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
import numpy as np
import praw
import tweepy
import requests
import xml.etree.ElementTree as ET  # built in library
from datetime import datetime

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from requests import get
from dataprod.config import Config, config

from django.utils.timezone import datetime, utc
from django.db.models import QuerySet

config: Config

reddit = praw.Reddit(
    client_id=config.reddit_client_id, client_secret=config.reddit_client_secret, user_agent=config.reddit_user_agent
)

twitter = tweepy.Client(bearer_token=config.twitter_bearer_token)


base_url = "https://yh-finance.p.rapidapi.com"
headers = {
    "X-RapidAPI-Key": config.yahoo_finance_header_key,
    "X-RapidAPI-Host": "yh-finance.p.rapidapi.com",
}


def calculate_indices(stock: models.Stock):
    prices = stock.price_set.all().order_by("timestamp").values_list("high", "low", "close")
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
    atr = AverageTrueRange(high=prices_df["high"], low=prices_df["low"], close=prices_df["close"])

    models.Indicator.objects.update_or_create(
        stock=stock, name="sma_50", defaults=dict(value=sma_50.sma_indicator().iloc[-1])
    )
    models.Indicator.objects.update_or_create(
        stock=stock, name="sma_100", defaults=dict(value=sma_100.sma_indicator().iloc[-1])
    )
    models.Indicator.objects.update_or_create(
        stock=stock, name="sma_200", defaults=dict(value=sma_200.sma_indicator().iloc[-1])
    )
    models.Indicator.objects.update_or_create(
        stock=stock, name="ema_50", defaults=dict(value=ema_50.ema_indicator().iloc[-1])
    )
    models.Indicator.objects.update_or_create(
        stock=stock, name="ema_100", defaults=dict(value=ema_100.ema_indicator().iloc[-1])
    )
    models.Indicator.objects.update_or_create(
        stock=stock, name="ema_200", defaults=dict(value=ema_200.ema_indicator().iloc[-1])
    )
    models.Indicator.objects.update_or_create(stock=stock, name="macd", defaults=dict(value=macd.macd_diff().iloc[-1]))
    models.Indicator.objects.update_or_create(stock=stock, name="rsi", defaults=dict(value=rsi.rsi().iloc[-1]))
    models.Indicator.objects.update_or_create(
        stock=stock, name="atr", defaults=dict(value=atr.average_true_range().iloc[-1])
    )


def calculate_indices(stock: models.Stock):
    prices = stock.price_set.all().order_by("timestamp").values_list("high", "low", "close")
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
    atr = AverageTrueRange(high=prices_df["high"], low=prices_df["low"], close=prices_df["close"])

    models.Indicator.objects.update_or_create(
        stock=stock, name="sma_50", defaults=dict(value=sma_50.sma_indicator().iloc[-1])
    )
    models.Indicator.objects.update_or_create(
        stock=stock, name="sma_100", defaults=dict(value=sma_100.sma_indicator().iloc[-1])
    )
    models.Indicator.objects.update_or_create(
        stock=stock, name="sma_200", defaults=dict(value=sma_200.sma_indicator().iloc[-1])
    )
    models.Indicator.objects.update_or_create(
        stock=stock, name="ema_50", defaults=dict(value=ema_50.ema_indicator().iloc[-1])
    )
    models.Indicator.objects.update_or_create(
        stock=stock, name="ema_100", defaults=dict(value=ema_100.ema_indicator().iloc[-1])
    )
    models.Indicator.objects.update_or_create(
        stock=stock, name="ema_200", defaults=dict(value=ema_200.ema_indicator().iloc[-1])
    )
    models.Indicator.objects.update_or_create(stock=stock, name="macd", defaults=dict(value=macd.macd_diff().iloc[-1]))
    models.Indicator.objects.update_or_create(stock=stock, name="rsi", defaults=dict(value=rsi.rsi().iloc[-1]))
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
    response = get(f"{base_url}/stock/v2/get-summary", headers=headers, params={"symbol": ticker})
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

    response = get(f"{base_url}/stock/v3/get-chart", headers=headers, params=querystring).json()
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
                ticker=data["ticker"], defaults=dict(name=data["name"], summary=data["summary"])
            )

            if stock:
                stock_data = get_yahoo_stock_price(ticker)
                for _, _open, high, low, close, timestamp in stock_data.itertuples():
                    models.Price.objects.update_or_create(
                        timestamp=timestamp, stock=stock, defaults=dict(open=_open, high=high, low=low, close=close)
                    )
                calculate_indices(stock)
            stock = models.Stock.objects.filter(ticker=ticker)
    return stock


# REDDIT SERVICES
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


# TWEETS
def get_tweets(query):
    query = "\$" + query + " lang:en"
    tweets = twitter.search_recent_tweets(
        query=query, tweet_fields=["author_id", "created_at", "public_metrics"], max_results=50
    )

    tweets_df = pd.DataFrame(tweets.data)
    pub_metrics = tweets_df["public_metrics"].apply(pd.Series)
    tweets_df = pd.concat([tweets_df, pub_metrics], axis=1)
    tweets_df.drop(columns=["public_metrics"], inplace=True)
    tweets_df["text"] = tweets_df["text"].apply(cleanTxt)

    # publicity score by summing pub metrics
    tweets_df["pub_score"] = tweets_df[["retweet_count", "reply_count", "like_count", "quote_count"]].sum(axis=1)
    # sort by publicity
    tweets_df.sort_values(by="pub_score", ascending=False, inplace=True)
    return tweets_df.sort_values(by="pub_score", ascending=False, inplace=True)


# NEWS
# functions from https://github.com/iAhsanJaved/FetchGoogleNews
def get_news(search_term, data_filter=None):
    """
    Search through Google News with the "search_term" and get the headlines
     and the contents of the news that was released today, this week, this month,
    or this year ("date_filter").
    """

    def get_text(x):
        start = x.find("<p>") + 3
        end = x.find("</p>")
        return x[start:end]

    url = clean_url(search_term, data_filter)
    response = requests.get(url)
    # get the root directly as we have text file of string now
    root = ET.fromstring(response.text)
    # get the required data
    title = [i.text for i in root.findall(".//channel/item/title")]
    link = [i.text for i in root.findall(".//channel/item/link")]
    description = [i.text for i in root.findall(".//channel/item/description")]
    pubDate = [i.text for i in root.findall(".//channel/item/pubDate")]
    source = [i.text for i in root.findall(".//channel/item/source")]
    # clear the description
    short_description = list(map(get_text, description))

    # set the data frame
    df = pd.DataFrame(
        {"title": title, "link": link, "description": short_description, "date": pubDate, "source": source}
    )
    # adjust the date column
    df.date = df.date.astype("datetime64")
    # for saving purpose uncomment the below
    df.to_csv(f"{search_term}_news.csv", encoding="utf-8-sig", index=False)
    return df


def clean_url(searched_item, data_filter):
    """
    OUTPUT : url to be fecthed for the searched_item and data_filter
     ---------------------------------------------------
    Parameters:
      today' - get headlines of the news that are released only in today
                       'this_week' - get headlines of the news that are released in this week
                       'this month' - news released in this month
                       'this_year' - news released in this year
                        number : int/str input for number of days ago
                        or '' blank to get all data
    """
    x = datetime.today()
    today = str(x)[:10]
    yesterday = str(x + pd.Timedelta(days=-1))[:10]
    this_week = str(x + pd.Timedelta(days=-7))[:10]
    if data_filter == "today":
        time = "after%3A" + yesterday
    elif data_filter == "this_week":
        time = "after%3A" + this_week + "+before%3A" + today
    elif data_filter == "this_year":
        time = "after%3A" + str(x.year - 1)
    elif str(data_filter).isdigit():
        temp_time = str(x + pd.Timedelta(days=-int(data_filter)))[:10]
        time = "after%3A" + temp_time + "+before%3A" + today
    else:
        time = ""
    url = f"https://news.google.com/rss/search?q={searched_item}+" + time + "&hl=en-US&ceid=US%3Aen"
    return url


# OTHERS
def sentiment_analysis(df, col_name="text"):
    # Assigning Initial Values
    positive = 0
    negative = 0
    neutral = 0
    # Creating empty lists
    tweet_list1 = []
    neutral_list = []
    negative_list = []
    positive_list = []

    # Iterating over the tweets in the dataframe
    for tweet in df[col_name]:
        tweet_list1.append(tweet)
        analyzer = SentimentIntensityAnalyzer().polarity_scores(tweet)
        neg = analyzer["neg"]
        pos = analyzer["pos"]

        if neg > pos:
            negative_list.append(tweet)  # appending the tweet that satisfies this condition
        elif pos > neg:
            positive_list.append(tweet)  # appending the tweet that satisfies this condition
        elif pos == neg:
            neutral_list.append(tweet)  # appending the tweet that satisfies this condition

    return positive_list, negative_list, neutral_list


def cleanTxt(text):
    text = re.sub("@[A-Za-z0–9]+", "", text)  # Removing @mentions
    text = re.sub("#", "", text)  # Removing '#' hash tag
    text = re.sub("RT[\s]+", "", text)  # Removing RT
    text = re.sub("https?:\/\/\S+", "", text)  # Removing hyperlink
    return text
