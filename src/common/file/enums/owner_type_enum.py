from enum import Enum

class OwnerTypeEnum(str, Enum):
    POST = "post"
    USER = "user"
    PRODUCT = "product"

# 모델별 ID 매핑을 사전으로 정의
OWNER_TYPE_MAPPING = {
    OwnerTypeEnum.POST: "post_id",  # post_id
    OwnerTypeEnum.USER: "user_id",  # user_id
    OwnerTypeEnum.PRODUCT: "product_id"  # product_id (예시)
}
