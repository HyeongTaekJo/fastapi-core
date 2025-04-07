from contextvars import ContextVar
from sqlalchemy.ext.asyncio import AsyncSession

# 전역 세션 저장용 ContextVar
_db_ctx_var: ContextVar[AsyncSession] = ContextVar("db_session")

# ✅ 세션을 ContextVar에 저장
def set_db_context(session: AsyncSession):
    _db_ctx_var.set(session)

# ✅ 세션을 ContextVar에서 꺼냄
def get_db_from_context() -> AsyncSession:
    return _db_ctx_var.get()
