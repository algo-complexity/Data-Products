from datetime import date, datetime
from typing import Dict, Literal, Optional, Union

from pydantic import BaseModel

from api import models


class Stock(BaseModel):
    name: str
    ticker: str
    summary: str
    image_url: Optional[str]

    @classmethod
    def from_orm(cls, stock: models.Stock):
        return cls(name=stock.name, ticker=stock.ticker, summary=stock.summary, image_url=stock.image_url)


class StockStub(BaseModel):
    name: str
    ticker: str

    @classmethod
    def from_orm(cls, stock: models.Stock):
        return cls(
            name=stock.name,
            ticker=stock.ticker,
        )


class Price(BaseModel):
    open: float
    high: float
    low: float
    close: float
    timestamp: datetime

    @classmethod
    def from_orm(cls, price: models.Price):
        return cls(
            open=price.open,
            high=price.high,
            low=price.low,
            close=price.close,
            timestamp=price.timestamp,
        )


class Reddit(BaseModel):
    title: str
    content: str
    timestamp: datetime
    author: str
    sentiment: Optional[Literal["positive", "negative", "neutral"]]
    score: int
    num_comments: int
    url: str

    @classmethod
    def from_orm(cls, reddit: models.Reddit):
        return cls(
            title=reddit.title,
            content=reddit.content,
            timestamp=reddit.timestamp,
            author=reddit.author,
            sentiment=reddit.sentiment,
            score=reddit.score,
            num_comments=reddit.num_comments,
            url=reddit.url,
        )


class Tweet(BaseModel):
    content: str
    timestamp: datetime
    author: str
    sentiment: Optional[Literal["positive", "negative", "neutral"]]
    retweets: int
    replies: int
    likes: int
    quotes: int
    pub_score: int
    hashtags: list[str]
    url: str

    @classmethod
    def from_orm(cls, tweet: models.Tweet):
        return cls(
            content=tweet.text,
            timestamp=tweet.created_at,
            author=tweet.author_id,
            sentiment=tweet.sentiment,
            retweets=tweet.retweet_count,
            replies=tweet.reply_count,
            likes=tweet.like_count,
            quotes=tweet.quote_count,
            pub_score=tweet.pub_score,
            hashtags=tweet.hashtags
            # hashtags split by space
        )


class News(BaseModel):
    headline: str
    url: str
    timestamp: datetime
    sentiment: Optional[Literal["positive", "negative", "neutral"]]
    source: str

    @classmethod
    def from_orm(cls, news: models.News):
        return cls(
            headline=news.title,
            url=news.link,
            timestamp=news.date,
            sentiment=news.sentiment,
            source=news.source,
        )


class Indicator(BaseModel):
    name: str
    value: float

    @classmethod
    def from_orm(cls, indicator: models.Indicator):
        return cls(
            name=indicator.name,
            value=indicator.value,
        )
