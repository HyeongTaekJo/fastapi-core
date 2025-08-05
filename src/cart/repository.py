from sqlalchemy import select
from sqlalchemy.orm import selectinload
from cart.model import CartModel, CartItemModel
from sqlalchemy.ext.asyncio import AsyncSession


class CartRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_cart_by_user_id(self, user_id: int) -> CartModel | None:
        """카트 조회 (없으면 None 반환)"""
        cart = await self.db.scalar(
            select(CartModel)
            .options(selectinload(CartModel.items))
            .where(CartModel.user_id == user_id)
        )
        return cart

    async def create_cart(self, user_id: int) -> CartModel:
        """카트 생성"""
        cart = CartModel(user_id=user_id)
        self.db.add(cart)
        # flush() 불필요, 커밋 시 반영
        return cart

    async def get_user_cart_dict(self, cart: CartModel) -> dict:
        """CartModel → dict 변환"""
        return {str(item.product_id): item.quantity for item in cart.items}

    async def save_user_cart(self, cart: CartModel, cart_dict: dict):
        """카트 저장"""
        # 기존 item 제거
        cart.items.clear()
        # 새로운 항목 추가
        for pid, qty in cart_dict.items():
            cart.items.append(CartItemModel(product_id=int(pid), quantity=qty))
        # flush/commit은 호출하는 쪽에서 처리
