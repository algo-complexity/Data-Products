from datetime import date
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
