# src/cache/dependencies.py
from redis.asyncio import Redis
from cache.redis_connection import redis

async def get_redis() -> Redis:
    return redis
