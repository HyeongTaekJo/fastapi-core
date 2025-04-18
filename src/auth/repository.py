from redis.asyncio import Redis
from cache.redis_context import get_redis_from_context
from typing import Optional
import time  


class AuthRepository:
    async def save_refresh_token(self, user_id: int, refresh_token: str):
        redis = get_redis_from_context()
        await redis.set(
            f"refresh:{user_id}",
            refresh_token,
            ex=60 * 60 * 24 * 7  # 7일
        )

    async def get_refresh_token(self, user_id: int) -> Optional[str]:
        redis = get_redis_from_context()
        token = await redis.get(f"refresh:{user_id}")
        return token.decode() if token else None
    
    async def delete_refresh_token(self, user_id: int):
        redis = get_redis_from_context()
        await redis.delete(f"refresh:{user_id}")
    
    async def is_blacklisted(self, token: str) -> bool:
        redis = get_redis_from_context()
        return await redis.exists(f"blacklist:{token}") == 1

    async def blacklist_token(self, token: str, exp: int):
        redis = get_redis_from_context()
        ttl = exp - int(time.time())
        if ttl > 0:
            await redis.setex(f"blacklist:{token}", ttl, "1")
