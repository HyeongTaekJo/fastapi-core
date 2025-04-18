# session_service.py

from fastapi import Request
from user.schemas.response import UserSchema

class SessionService:
    @staticmethod
    def merge_cart(redis_cart: dict, db_cart: dict) -> dict:
        merged = db_cart.copy()
        for pid, qty in redis_cart.items():
            merged[pid] = merged.get(pid, 0) + qty
        return merged

    @staticmethod
    async def update_session(request: Request, user: UserSchema, merged_cart: dict):
        session = request.state.session
        session["user"] = user.model_dump()
        session["cart"] = merged_cart
