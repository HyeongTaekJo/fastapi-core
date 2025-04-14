import logging
from fastapi import Request
from database.mysql_connection import async_session_maker
from database.session_context import set_db_context
from common.middleware.error import middleware_error_handler

logger = logging.getLogger(__name__)

async def db_session_middleware(request: Request, call_next):
    """DB 세션을 컨텍스트에 주입하는 미들웨어"""
    session = None
    try:
        session = async_session_maker()
        set_db_context(session)  # ContextVar에 저장
        response = await call_next(request)
        await session.commit()
        return response
    except Exception as e:
        if session:
            await session.rollback()
        logger.warning(f"[DB_SESSION] 처리 실패: {e}")
        return middleware_error_handler(e)
    finally:
        if session:
            await session.close() 