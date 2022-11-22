import re
import xml.etree.ElementTree as ET  # built in library
from typing import Optional

import numpy as np
import pandas as pd
import praw
import requests
import tweepy
from django.db.models import QuerySet
from django.utils.timezone import datetime, timedelta, utc
from nltk.sentiment.vader import SentimentIntensityAnalyzer
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

twitter = tweepy.Client(bearer_token=config.twitter_bearer_token)


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
    response = requests.get(
        f"{base_url}/auto-complete", headers=headers, params={"q": search}
    )
    quotes = response.json()["quotes"]
    if quotes == []:
        return None
    return quotes[0]["symbol"]


def get_yahoo_stock_data(ticker: str) -> dict:
    response = requests.get(
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

    response = requests.get(
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
                image_url=get_image_url(data["name"]),
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
    for post in reddit.subreddit(subreddit).search(symb, time_filter=time):
        if post.is_self:
            posts.append(
                [
                    post.title,
                    post.selftext,
                    datetime.fromtimestamp(post.created, tz=utc),
                    post.author.name,
                    get_sentiment(post.selftext),
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


# TWEETS
def get_tweets(query) -> pd.DataFrame:
    """Returns a dataframe of tweets matching a given search query.

    Args:
        query (str): Search query eg. AAPL

    Returns:
        pd.DataFrame: DataFrame of tweets and other relevant information.
    """
    query = f"\\${query} lang:en"
    tweets = twitter.search_recent_tweets(
        query=query,
        tweet_fields=["author_id", "created_at", "public_metrics", "entities"],
        max_results=100,
    )

    tweets_df = pd.DataFrame(tweets.data)

    # explode out public metrics
    pub_metrics = tweets_df["public_metrics"].apply(pd.Series)

    # extract hashtags
    entities = pd.json_normalize(tweets_df["entities"])
    hashtags = []
    for i in entities["hashtags"]:
        if isinstance(i, list):
            hashtags.append(" ".join([j["tag"] for j in i]))
    hashtags = pd.Series(hashtags).rename("hashtags")

    tweets_df = pd.concat([tweets_df, hashtags, pub_metrics], axis=1)
    tweets_df.drop(
        columns=["public_metrics", "edit_history_tweet_ids", "entities"], inplace=True
    )
    tweets_df["text"] = tweets_df["text"].apply(cleanTxt)
    tweets_df["url"] = tweets_df["id"].apply(
        lambda x: "https://twitter.com/twitter/status/" + str(x)
    )

    # publicity score by summing pub metrics
    tweets_df["pub_score"] = tweets_df[
        ["retweet_count", "reply_count", "like_count", "quote_count"]
    ].sum(axis=1)
    tweets_df["sentiment"] = tweets_df["text"].apply(get_sentiment)

    # sort by publicity
    tweets_df.sort_values(by="pub_score", ascending=False, inplace=True)
    return tweets_df


# NEWS
# functions from https://github.com/iAhsanJaved/FetchGoogleNews
def get_news(search_term, data_filter=None) -> pd.DataFrame:
    """Search through Google News with the "search_term" and get the headlines
    and the contents of the news that was released today, this week, this month,
    or this year ("date_filter").

    Args:
        search_term (str): Symbol/search query to search
        data_filter (str, optional): Date window - "today", "this_week", "this_month", "this_year". Defaults to None.

    Returns:
        pd.DataFrame: DataFrame of news and other relevant information.
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
        {
            "title": title,
            "link": link,
            "description": short_description,
            "date": pubDate,
            "source": source,
        }
    )
    # adjust the date column
    df["date"] = df["date"].astype("datetime64")
    df["sentiment"] = df["title"].apply(get_sentiment)
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
    today = x.date().isoformat()
    yesterday = (x - timedelta(days=1)).date().isoformat()
    this_week = (x - timedelta(days=7)).date().isoformat()
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
    url = (
        f"https://news.google.com/rss/search?q={searched_item}+"
        + time
        + "&hl=en-US&ceid=US%3Aen"
    )
    return url


# OTHERS
def get_sentiment(text):
    """Returns a discrete value (pos/neg/neutral) describing the sentiment of a given input text.

    Args:
        text (str): Input text to analyze.

    Returns:
        str: One of ("positive", "negative", "neutral")
    """

    # Iterating over the tweets in the dataframe
    analyzer = SentimentIntensityAnalyzer().polarity_scores(text)
    neg = analyzer["neg"]
    pos = analyzer["pos"]

    if neg > pos:
        return "negative"
    elif pos > neg:
        return "positive"
    elif pos == neg:
        return "neutral"


def cleanTxt(text):
    text = re.sub(r"@[A-Za-z0–9]+", "", text)  # Removing @mentions
    text = re.sub(r"#", "", text)  # Removing '#' hash tag
    text = re.sub(r"RT[\s]+", "", text)  # Removing RT
    text = re.sub(r"https?:\/\/\S+", "", text)  # Removing hyperlink
    return text
