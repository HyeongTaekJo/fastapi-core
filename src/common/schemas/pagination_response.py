from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar("T")

class CursorPaginationResult(BaseModel, Generic[T]):
    data: List[T]
    count: int
    cursor: Optional[dict]
    next: Optional[str]

class PagePaginationResult(BaseModel, Generic[T]):
    data: List[T]
    total: int
