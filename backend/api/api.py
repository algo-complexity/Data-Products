from django.shortcuts import get_object_or_404
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