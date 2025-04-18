from fastapi import APIRouter, Request, Depends
from typing import Optional
from cart.service import CartService
from cart.schemas.request import AddCartSchema, UpdateCartSchema, RemoveCartSchema
from user.model import UserModel
from user.dependencies.optional_user import get_optional_user

router = APIRouter(prefix="/cart", tags=["cart"])

# 장바구니는 1개씩만 수정, 추가, 삭제 가능하다.

# 장바구니 조회
@router.get("/")
async def get_cart(
    request: Request,
    user: Optional[UserModel] = Depends(get_optional_user),
    cart_service: CartService = Depends()
):
    return await cart_service.get_cart(request, user)

# 장바구니 항목 추가
@router.post("/add")
async def add_to_cart(
    request: Request,
    data: AddCartSchema,
    user: Optional[UserModel] = Depends(get_optional_user),
    cart_service: CartService = Depends()
):
    return await cart_service.add_item(request, user, data)

# 장바구니 항목 수정
@router.put("/update")
async def update_cart_item(
    request: Request,
    data: UpdateCartSchema,
    user: Optional[UserModel] = Depends(get_optional_user),
    cart_service: CartService = Depends()
):
    return await cart_service.update_item(request, user, data)

# 장바구니 항목 제거
@router.delete("/delete")
async def remove_cart_item(
    request: Request,
    data: RemoveCartSchema,
    user: Optional[UserModel] = Depends(get_optional_user),
    cart_service: CartService = Depends()
):
    return await cart_service.remove_item(request, user, data)
