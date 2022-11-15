from datetime import date, datetime
from typing import Dict, Literal, Optional, Union

from pydantic import BaseModel

from api import models

class Stock(BaseModel):
    name: str
    ticker: str
    summary: str

    @classmethod
    def from_orm(cls, stock: models.Stock):
        return cls(
            name=stock.name,
            ticker=stock.ticker,
            summary=stock.summary
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
    sentiment: Optional[str]
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

class Indicator(BaseModel):
    name: str
    value: float

    @classmethod
    def from_orm(cls, indicator: models.Indicator):
        return cls(
            name=indicator.name,
            value=indicator.value,
        )

