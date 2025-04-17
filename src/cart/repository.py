from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from database.session_context import get_db_from_context
from cart.model import CartModel, CartItemModel
from sqlalchemy.ext.asyncio import AsyncSession

class CartRepository:
    def __init__(self):
        self.session: AsyncSession = get_db_from_context()

    async def get_or_create_cart(self, user_id: int) -> CartModel:
        cart = await self.session.scalar(
            select(CartModel)
            .options(selectinload(CartModel.items))
            .where(CartModel.user_id == user_id)
        )
        if cart:
            return cart

        cart = CartModel(user_id=user_id)
        self.session.add(cart)
        await self.session.flush()  # id 생성
        return cart

    async def get_user_cart_dict(self, user_id: int) -> dict:
        cart = await self.get_or_create_cart(user_id)
        return {
            str(item.product_id): item.quantity
            for item in cart.items
        }

    async def save_user_cart(self, user_id: int, cart_dict: dict):
        cart = await self.get_or_create_cart(user_id)

        # 기존 item 모두 제거
        cart.items.clear()

        # 새 항목 추가
        for pid, qty in cart_dict.items():
            cart.items.append(CartItemModel(product_id=int(pid), quantity=qty))

        await self.session.flush()
