# src/common/lifecycle/startup_check.py

import logging
from sqlalchemy import text
from redis.exceptions import RedisError

from database.mysql_connection import async_session_maker
from cache.redis_connection import redis

logger = logging.getLogger(__name__)

async def test_db_connection():
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        logger.info(" Database connected successfully")
    except Exception as e:
        logger.critical(f"❌ Database connection failed: {e}")
        raise e

async def test_redis_connection():
    try:
        await redis.set("__ping__", "pong", ex=5)
        result = await redis.get("__ping__")
        if result != b"pong":
            raise RedisError("Invalid Redis response")
        logger.info(" Redis connected successfully")
    except Exception as e:
        logger.critical(f"❌ Redis connection failed: {e}")
        raise e
