from typing import Optional, Literal
from pydantic import BaseModel, Field

class BasePaginationSchema(BaseModel):
    page: Optional[int] = Field(default=None, description="Page-based pagination")
    take: int = Field(default=20, description="Number of items per request")
    where__id__less_than: Optional[int] = None
    where__id__more_than: Optional[int] = None
    order__id: Optional[Literal['ASC', 'DESC']] = 'ASC'