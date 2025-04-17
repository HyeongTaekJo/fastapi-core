# src/common/models_registry.py

# 모든 모델 import (순환 참조 피하기 위해 여기서 한 번에 처리)
from cart.model import CartItemModel
from product.model import ProductModel
from order.model import OrderModel
from user.model import UserModel
from post.model import PostModel

# Base는 공통 정의된 곳에서 import
from common.model.base_model import Base

__all__ = [
    "Base",
    "CartItemModel",
    "ProductModel",
    "OrderModel",
    "UserModel",
    "PostModel",
]
