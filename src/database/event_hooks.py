# src/database/event_hooks.py

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine
from database.mysql_connection import async_engine

# @event.listens_for(async_engine.sync_engine, "begin")
# def before_transaction_begin(conn):
#     print("🔥 [트랜잭션 시작] conn:", conn)

# @event.listens_for(async_engine.sync_engine, "commit")
# def before_transaction_commit(conn):
#     print("✅ [트랜잭션 커밋] conn:", conn)

# @event.listens_for(async_engine.sync_engine, "rollback")
# def before_transaction_rollback(conn):
#     print("❌ [트랜잭션 롤백] conn:", conn)
