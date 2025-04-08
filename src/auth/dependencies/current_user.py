from fastapi import Request, HTTPException, Depends
from user.repository import UserRepository
from user.schemas.response import UserSchema
from user.model.model import UserModel
from cache.redis_context import get_redis_from_context
import json

import logging

logger = logging.getLogger(__name__)


async def get_current_user(
    request: Request,
    user_repository: UserRepository = Depends()
) -> UserModel:
    
    redis = get_redis_from_context()  # 미들웨어에서 주입된 Redis 사용
    user_id = getattr(request.state, "user_id", None) # 
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    redis_key = f"user:{user_id}"
    cached = await redis.get(redis_key)

    if cached:
        try:
            user_data = json.loads(cached)
            # ORM으로 쓰려면 Pydantic → SQLAlchemy 변환 필요 (아래는 간단히 Pydantic 반환)
            return UserSchema(**user_data)
        except Exception as e:
            logger.warning(f"Redis 사용자 캐싱 복원 실패: {e}")  # 로깅 추천

    # fallback: DB에서 조회
    user = await user_repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Redis에 캐싱 (dict 형태로)
    user_dict = UserSchema.model_validate(user).model_dump()
    await redis.setex(redis_key, 3600, json.dumps(user_dict))
    return user
