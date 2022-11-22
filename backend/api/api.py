from typing import Literal

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from ninja import Router

from schemas import PaginatedList, paginate

from . import models, schemas, services

router = Router()


@router.get("/stock", response=PaginatedList[schemas.Stock])
def get_stocks(request, page: int = 1, limit: int = 10):
    results = models.Stock.objects.all()
    return paginate(results, schemas.Stock, page, limit)


@router.get("/stock/search", response=PaginatedList[schemas.StockStub])
def get_stock_search(request, q: str = None, page: int = 1, limit: int = 10):
    results = models.Stock.objects.all()
    if q:
        results = results.fuzzy_search(q)
        if not results.exists():
            results = services.get_stock_from_yahoo(q)
    return paginate(results, schemas.StockStub, page, limit)


@router.get("/stock/{str:ticker}", response=schemas.Stock)
def get_stock(request, ticker: str):
    stock = get_object_or_404(models.Stock, ticker=ticker)
    return schemas.Stock.from_orm(stock)


@router.get("/stock/{str:ticker}/price", response=list[schemas.Price])
def get_stock_price(request, ticker: str):
    results = models.Price.objects.filter(stock__ticker=ticker).order_by("-timestamp")[
        :252
    ]
    return [schemas.Price.from_orm(price) for price in results]


@router.get("/stock/{str:ticker}/reddit", response=PaginatedList[schemas.Reddit])
def get_stock_reddit(request, ticker: str, page: int = 1, limit: int = 10):
    results = models.Reddit.objects.filter(stock__ticker=ticker)
    return paginate(results, schemas.Reddit, page, limit)


@router.get("/stock/{str:ticker}/tweets", response=PaginatedList[schemas.Tweet])
def get_stock_tweets(request, ticker: str, page: int = 1, limit: int = 10):
    results = models.Tweet.objects.filter(stock__ticker=ticker)
    return paginate(results, schemas.Tweet, page, limit)


@router.get("/stock/{str:ticker}/news", response=PaginatedList[schemas.News])
def get_stock_news(request, ticker: str, page: int = 1, limit: int = 10):
    results = models.News.objects.filter(stock__ticker=ticker)
    return paginate(results, schemas.News, page, limit)


@router.get("/stock/{str:ticker}/indicators", response=list[schemas.Indicator])
def get_stock_indicators(request, ticker: str):
    results = models.Indicator.objects.filter(stock__ticker=ticker)
    return [schemas.Indicator.from_orm(price) for price in results]


@router.get("/stock/{str:ticker}/sentiment", response=list[schemas.PieValue])
def get_stock_sentiment(
    request, ticker: str, q: Literal["tweet", "reddit", "news"] = "tweet"
):

    results = (
        models.Stock.objects.filter(ticker=ticker)
        .annotate(
            negative=Count(
                f"{q}__sentiment",
                filter=Q(**{f"{q}__sentiment": models.SentimentChoices.NEGATIVE}),
            ),
            positive=Count(
                f"{q}__sentiment",
                filter=Q(**{f"{q}__sentiment": models.SentimentChoices.POSITIVE}),
            ),
            neutral=Count(
                f"{q}__sentiment",
                filter=Q(**{f"{q}__sentiment": models.SentimentChoices.NEUTRAL}),
            ),
        )
        .first()
    )

    return [
        schemas.PieValue(key=key, value=getattr(results, key))
        for key in ["positive", "neutral", "negative"]
    ]
