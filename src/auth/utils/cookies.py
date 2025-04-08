from fastapi import Response
from common.const.settings import settings  # .env에서 환경 불러오기

# 7일 동안 유지되는 refresh token 쿠키 설정
def set_refresh_token_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,                          # JavaScript에서 접근 불가 (XSS 방지)
        secure=(settings.ENV == "production"),  # HTTPS 환경에서만 전송됨 (MITM 방지)
        samesite="Strict",                      # CSRF 방지 (Strict | Lax | None)
        max_age=60 * 60 * 24 * 7,               # 7일
        path="/",                               # 전체 경로에서 사용 가능
    )