from fastapi import Request, HTTPException
import logging

logger = logging.getLogger(__name__)

async def get_current_cart(request: Request) -> dict[int, int]:
    """
    ✅ Redis 세션에서 현재 사용자의 장바구니(cart)를 꺼내는 의존성 함수
    - 세션에 'cart'가 없으면 빈 dict 반환
    - 구조: {product_id: quantity}
    """
    session = getattr(request.state, "session", {})
    cart_data = session.get("cart")

    if cart_data is None:
        logger.info("🛒 [CART] 세션에 장바구니 정보가 없음 → 빈 장바구니 반환")
        return {}

    try:
        return {int(k): int(v) for k, v in cart_data.items()}  # ✅ 타입 안정성 보장
    except Exception as e:
        logger.warning(f"❌ [CART] 장바구니 파싱 실패: {e}")
        raise HTTPException(status_code=400, detail="장바구니 정보가 손상되었습니다.")
