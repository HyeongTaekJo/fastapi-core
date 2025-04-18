from typing import Optional, Union
from fastapi import Request
from user.schemas.response import UserSchema

# session_service.py

class SessionService:
    @staticmethod
    def merge_cart(redis_cart: dict, db_cart: dict) -> dict:
        """
        Redis 장바구니와 DB 장바구니를 병합한다.
        - 양쪽에 같은 상품이 있으면 수량이 큰 쪽 선택
        - 한 쪽에만 있으면 그대로 채택
        """
        merged = db_cart.copy()  # DB 기준 복사

        for pid, qty in redis_cart.items():
            try:
                redis_qty = int(qty)
            except (ValueError, TypeError):
                redis_qty = 0

            db_qty = merged.get(pid, 0)
            merged[pid] = max(redis_qty, db_qty)

        return merged

    @staticmethod
    async def update_session(
        request: Request,
        user: Optional[Union[UserSchema, dict]] = None,
        merged_cart: Optional[dict] = None
    ):
        session = request.state.session

        if user is not None:
            session["user"] = user.model_dump() if hasattr(user, "model_dump") else user

        if merged_cart is not None:
            session["cart"] = merged_cart
