from redis.asyncio import Redis
from common.utils.redis_context import get_redis_from_context

class AuthRepository:
    def __init__(self):
        self.redis = get_redis_from_context()

    async def save_refresh_token(self, user_id: int, refresh_token: str):
        await self.redis.set(
            f"refresh:{user_id}",
            refresh_token,
            ex=60 * 60 * 24 * 7  # 7일
        )