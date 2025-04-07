from redis.asyncio import Redis
from common.utils.redis_context import get_redis_from_context
from typing import Optional


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