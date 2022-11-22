from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

from api import models


class Stock(BaseModel):
    name: str
    ticker: str
    summary: str
    image_url: Optional[str]

    @classmethod
    def from_orm(cls, stock: models.Stock):
        return cls(
            name=stock.name,
            ticker=stock.ticker,
            summary=stock.summary,
            image_url=stock.image_url,
        )


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
            content=tweet.content,
            timestamp=tweet.timestamp,
            author=tweet.author,
            url=tweet.url,
            sentiment=tweet.sentiment,
            retweets=tweet.retweets,
            replies=tweet.replies,
            likes=tweet.likes,
            quotes=tweet.quotes,
            pub_score=tweet.pub_score,
            hashtags=tweet.hashtags.split(),
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
            headline=news.headline,
            url=news.url,
            timestamp=news.timestamp,
            sentiment=news.sentiment,
            source=news.source,
        )


class Indicator(BaseModel):
    name: str
    value: Literal["positive", "negative", "neutral"]

    @classmethod
    def from_orm(cls, indicator: models.Indicator):
        return cls(
            name=indicator.name,
            value=indicator.value,
        )
