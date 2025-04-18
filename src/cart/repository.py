from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from database.session_context import get_db_from_context
from cart.model import CartModel
from cart.model import CartItemModel

class CartRepository:
    async def get_or_create_cart(self, user_id: int) -> CartModel:
        session = get_db_from_context()
        cart = await session.scalar(
            select(CartModel)
            .options(selectinload(CartModel.items))
            .where(CartModel.user_id == user_id)
        )
        if cart:
            return cart

        cart = CartModel(user_id=user_id)
        session.add(cart)
        await session.flush()  # id 생성
        return cart

    async def get_user_cart_dict(self, user_id: int) -> dict:
        # session = get_db_from_context()
        cart = await self.get_or_create_cart(user_id)
        return {
            str(item.product_id): item.quantity
            for item in cart.items
        }

    async def save_user_cart(self, user_id: int, cart_dict: dict):
        cart = await self.get_or_create_cart(user_id)
        session = get_db_from_context()

        if session.in_transaction():
            print("🧾 레포지토리에서 세션 확인됨! 이미 트랜잭션 있음")
        else:
            print("🚨 레포지토리 진입 시 트랜잭션 없음 → 문제가 될 수 있음")

        # 기존 item 모두 제거
        cart.items.clear()

        # 새 항목 추가
        for pid, qty in cart_dict.items():
            cart.items.append(CartItemModel(product_id=int(pid), quantity=qty))

        await session.flush()
