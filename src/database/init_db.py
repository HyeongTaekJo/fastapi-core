# src/database/init_db.py
from common.model.models_registry import Base
from .mysql_connection import async_engine

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
