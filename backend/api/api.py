from django.shortcuts import get_object_or_404
from django.utils.timezone import now, timedelta
from ninja import Router

from schemas import PaginatedList, paginate

from . import models, schemas, services

router = Router()

@router.get("/stock", response=PaginatedList[schemas.Stock])
def get_researchers(request, page: int = 1, limit: int = 10):
    results = models.Stock.objects.all()
    return paginate(results, schemas.Stock, page, limit)


@router.get("/stock/search", response=PaginatedList[schemas.StockStub])
def get_researcher_search(request, q: str = None, page: int = 1, limit: int = 10):
    results = models.Stock.objects.all()
    if q:
        results = results.fuzzy_search(q)
        if not results.exists():
            results = services.get_stock_from_yahoo(q)
    return paginate(results, schemas.StockStub, page, limit)

@router.get("/stock/{str:ticker}", response=schemas.Stock)
def get_researcher_name(request, ticker: str):
    stock = get_object_or_404(models.Stock, ticker=ticker)
    return schemas.Stock.from_orm(stock)

@router.get("/stock/{str:ticker}/price", response=list[schemas.Price])
def get_researcher_name(request, ticker: str):
    results = models.Price.objects.filter(stock__ticker=ticker, timestamp__gte=now() - timedelta(days=6*30))
    return [schemas.Price.from_orm(price) for price in results]


@router.get("/stock/{str:ticker}/reddit", response=PaginatedList[schemas.Reddit])
def get_researcher_name(request, ticker: str, page: int = 1, limit: int = 10):
    results = models.Reddit.objects.filter(stock__ticker=ticker)
    return paginate(results, schemas.Reddit, page, limit)