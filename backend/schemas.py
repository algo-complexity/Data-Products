from typing import Generic, Literal, Protocol, TypeVar

from django.core.paginator import Paginator
from django.db.models import QuerySet
from pydantic import BaseModel
from pydantic.generics import GenericModel

PaginatedListItem = TypeVar("PaginatedListItem")


class PaginatedList(GenericModel, Generic[PaginatedListItem]):
    items: list[PaginatedListItem]
    limit: int
    total: int
    page: int
    pages: int


class SchemaFactory(Protocol):
    def from_orm(self, model) -> BaseModel:
        pass


def paginate(
    manager_or_qs,
    schema: SchemaFactory,
    page: int = 1,
    limit: int = 50,
    order_by: list[str] = None,
    default_order_by: list[str] = None,
):
    """
    If `order_by` is provided, results will be ordered by `order_by`. Otherwise, if `manager_or_qs` is not already
    ordered, results will be ordered by `default_order_by`, which defaults to `["pk"]`.
    """
    if default_order_by is None:
        default_order_by = ["pk"]
    qs = manager_or_qs if isinstance(manager_or_qs, QuerySet) else manager_or_qs.all()
    if order_by:
        qs = qs.order_by(*order_by)
    elif not qs.query.order_by:
        qs = qs.order_by(*default_order_by)
    paginator = Paginator(qs, limit)
    page = paginator.get_page(page)
    items = [schema.from_orm(f) for f in page.object_list]
    return PaginatedList(
        items=items,
        limit=limit,
        total=paginator.count,
        page=page.number,
        pages=paginator.num_pages,
    )


Data = TypeVar("Data")
_NOT_SET = object()


class SuccessResponse(GenericModel, Generic[Data]):
    success: Literal[True] = True
    data: Data = {}

    @classmethod
    def with_data(cls, data: Data = _NOT_SET):
        return cls(data=data)


class ErrorDetail(BaseModel):
    # computer-readable error code, eg. "not_found"
    code: str

    # human-readable message for the error
    message: str


class ErrorResponse(GenericModel, Generic[Data]):
    success: Literal[False] = False
    error: ErrorDetail
    data: Data = {}

    @classmethod
    def with_detail(cls, code: str, message: str, data: Data = _NOT_SET):
        if data is not _NOT_SET:
            return cls(error=ErrorDetail(code=code, message=message), data=data)
        return cls(error=ErrorDetail(code=code, message=message))

    @classmethod
    def not_found(cls):
        return cls.with_detail("not_found", "Not found")


ValidationErrors = dict[str, str]


class ValidationErrorResponse(ErrorResponse[ValidationErrors]):
    @classmethod
    def with_errors(cls, errors: ValidationErrors):
        return cls.with_detail(
            code="validation_error", message="Validation errors", data=errors
        )
