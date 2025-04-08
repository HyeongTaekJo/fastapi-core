from redis.asyncio import Redis
from common.utils.redis_context import get_redis_from_context
from typing import Optional
import time  


class AuthRepository:
    def __init__(self):
        self.redis = get_redis_from_context()

    async def save_refresh_token(self, user_id: int, refresh_token: str):
        await self.redis.set(
            f"refresh:{user_id}",
            refresh_token,
            ex=60 * 60 * 24 * 7  # 7일
        )

    async def get_refresh_token(self, user_id: int) -> Optional[str]:
        token = await self.redis.get(f"refresh:{user_id}")
        return token.decode() if token else None
    
    async def delete_refresh_token(self, user_id: int):
        await self.redis.delete(f"refresh:{user_id}")
    
    async def is_blacklisted(self, token: str) -> bool:
        return await self.redis.exists(f"blacklist:{token}") == 1

    async def blacklist_token(self, token: str, exp: int):
        ttl = exp - int(time.time())
        if ttl > 0:
            await self.redis.setex(f"blacklist:{token}", ttl, "1")