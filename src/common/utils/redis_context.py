from contextvars import ContextVar
from redis.asyncio import Redis

_redis_ctx_var: ContextVar[Redis] = ContextVar("redis")

def set_redis_context(redis: Redis):
    _redis_ctx_var.set(redis)

def get_redis_from_context() -> Redis:
    return _redis_ctx_var.get()
