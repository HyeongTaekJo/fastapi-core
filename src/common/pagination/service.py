from typing import Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc, func
from urllib.parse import urlencode
from common.pagination.schemas.pagination_request import BasePaginationSchema
from common.pagination.schemas.pagination_response import PagePaginationResult, CursorPaginationResult
from common.const.filter_mapper import FILTER_MAPPER
import os
import uuid
from fastapi import UploadFile, HTTPException
from starlette import status
from fastapi.responses import JSONResponse
from pathlib import Path
from common.const.file_consts import ALLOWED_IMAGE_EXTENSIONS
from common.const.path_consts import TEMP_FOLDER_PATH
import aiofiles
from cache.redis_connection import redis


from common.const.settings import settings  # settings 직접 import


class CommonService:
    async def paginate(
        self,
        request: BasePaginationSchema,
        model: Type,
        session: AsyncSession,
        base_query=None,
        path: str = "",
    ):
        if request.page:
            return await self.page_paginate(request, model, session, base_query)
        return await self.cursor_paginate(request, model, session, base_query, path)

    async def page_paginate(self, request, model, session, base_query=None):
        query = base_query if base_query is not None else select(model)
        query = self.apply_filters(query, model, request)

        total = await session.scalar(select(func.count()).select_from(query.subquery()))
        query = query.order_by(
            asc(model.id) if request.order__id == "ASC" else desc(model.id)
        )
        query = query.limit(request.take).offset(request.take * (request.page - 1))
        result = await session.execute(query)
        data = result.scalars().all()

        return PagePaginationResult(data=data, total=total)

    async def cursor_paginate(self, request, model, session, base_query=None, path=""):
        query = base_query if base_query is not None else select(model)
        query = self.apply_filters(query, model, request)

        query = query.order_by(
            asc(model.id) if request.order__id == "ASC" else desc(model.id)
        ).limit(request.take)

        result = await session.execute(query)
        items = result.scalars().all()
        last_item = items[-1] if len(items) == request.take else None

        next_url = None
        if last_item:
            params = request.model_dump(exclude_none=True)
            key = "where__id__more_than" if request.order__id == "ASC" else "where__id__less_than"
            params[key] = last_item.id

            next_url = f"{settings.PROTOCOL}://{settings.HOST}:{settings.PORT}/{path}?{urlencode(params)}"


        return CursorPaginationResult(
            data=items,
            count=len(items),
            cursor={"after": last_item.id if last_item else None},
            next=next_url,
        )

    def apply_filters(self, query, model, dto: BasePaginationSchema):
        for key, value in dto.model_dump(exclude_none=True).items():
            if key.startswith("where__"):
                parts = key.split("__")
                column = getattr(model, parts[1], None)
                if not column:
                    continue

                if len(parts) == 2:
                    query = query.where(column == value)
                elif len(parts) == 3:
                    op = parts[2]
                    func = FILTER_MAPPER.get(op)
                    if not func:
                        raise ValueError(f"Unsupported filter operator: {op}")

                    if op == "between":
                        # 넘기기만 하고 가공하지 않음
                        query = query.where(func(column, value))
                    elif op == "i_like":
                        query = query.where(func(column, f"%{value}%"))
                    else:
                        query = query.where(func(column, value))
        return query
    