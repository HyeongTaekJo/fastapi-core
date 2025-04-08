# database/redis_connection.py
from redis.asyncio import Redis, BlockingConnectionPool
from common.const.settings import settings

pool = BlockingConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    max_connections=30,
    timeout=3,
)

redis = Redis(connection_pool=pool, decode_responses=True)

# 💡 동작 흐름
# 클라이언트 요청이 들어옴

# 커넥션 30개 중 30개가 이미 사용 중이라면?

# 31번째 요청은 최대 3초 동안 기다림

# 3초 이내에 누군가 커넥션을 반납하면, 그 커넥션을 사용

# 3초가 지나도 반납된 커넥션이 없다면?
# 👉 TimeoutError 또는 ConnectionTimeout 에러 발생

