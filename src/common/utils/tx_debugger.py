# 📁 src/common/utils/tx_debugger.py

from database.session_context import get_db_from_context
import logging

logger = logging.getLogger(__name__)

def log_tx_state(location: str):
    session = get_db_from_context()

    logger.debug(
        f"[🔍 {location}] "
        f"session_id={id(session)} | "
        f"in_transaction={session.in_transaction()} | "
        f"dirty={list(session.dirty)} | "
        f"new={list(session.new)} | "
        f"deleted={list(session.deleted)}"
    )


# 디버깅 하기 좋음
# 사용법 : log_tx_state( "트랜잭션 시작")