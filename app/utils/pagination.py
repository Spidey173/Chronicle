"""Pagination helper utility."""

from math import ceil
from typing import Any, List, Optional, Type, TypeVar
from sqlalchemy.orm import Query
from pydantic import BaseModel
from app.schemas.common import PaginatedResponse, PaginationMeta

T = TypeVar("T", bound=BaseModel)


def paginate_query(
    query: Query,
    page: int = 1,
    page_size: int = 20,
    schema_cls: Optional[Type[T]] = None,
) -> PaginatedResponse[Any]:
    """Execute paginated query and return PaginatedResponse."""
    page = max(1, page)
    page_size = min(max(1, page_size), 100)

    total_records = query.count()
    total_pages = ceil(total_records / page_size) if total_records > 0 else 1

    items_raw = query.offset((page - 1) * page_size).limit(page_size).all()

    if schema_cls:
        items = [schema_cls.model_validate(item) for item in items_raw]
    else:
        items = items_raw

    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total_records=total_records,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )

    return PaginatedResponse(items=items, pagination=pagination)
