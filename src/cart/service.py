from fastapi import Request, HTTPException
from typing import Optional
from cart.repository import CartRepository
from cart.schemas.request import AddCartSchema, UpdateCartSchema, RemoveCartSchema
from cache.session_service import SessionService
from user.model import UserModel
from sqlalchemy.ext.asyncio import AsyncSession

class CartService:
    def __init__(self):
        self.repo = CartRepository()
        self.session_service = SessionService()

    # 장바구니 조회
    async def get_cart(self, request: Request, user: Optional[UserModel]):
        return request.state.session.get("cart", {})

    # 장바구니 추가
    async def add_item(
        self, 
        request: Request, 
        user: Optional[UserModel], 
        data: AddCartSchema,
    ):
        cart = request.state.session.get("cart", {})
        cart[str(data.product_id)] = cart.get(str(data.product_id), 0) + data.quantity

        await self.session_service.update_session(request, user, cart)

        return {"detail": "장바구니에 추가되었습니다.", "cart": cart}

    # 장바구니 수정
    async def update_item(
        self, 
        request: Request, 
        user: Optional[UserModel], 
        data: UpdateCartSchema
    ):
        cart = request.state.session.get("cart", {})

        if str(data.product_id) not in cart:
            raise HTTPException(400, detail="장바구니에 해당 상품이 없습니다.")

        if data.quantity > 0:
            cart[str(data.product_id)] = data.quantity
        else:
            cart.pop(str(data.product_id))

        await self.session_service.update_session(request, user, cart)

        return {"detail": "장바구니가 수정되었습니다.", "cart": cart}

    # 장바구니 삭제
    async def remove_item(
        self, 
        request: Request, 
        user: Optional[UserModel], 
        data: RemoveCartSchema
    ):
        cart = request.state.session.get("cart", {})

        if str(data.product_id) not in cart:
            raise HTTPException(400, detail="장바구니에 해당 상품이 없습니다.")

        cart.pop(str(data.product_id))

        await self.session_service.update_session(request, user, cart)

        return {"detail": "장바구니에서 제거되었습니다.", "cart": cart}
