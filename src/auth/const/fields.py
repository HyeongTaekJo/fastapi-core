# 로그인용 경로 매핑
LOGIN_TYPE_FIELD_MAP = {
    "/login/email": "email",
    "/login/login_id": "login_id",
    "/login/phone": "phone"
}

# 회원가입 시 유니크 검증 필드
UNIQUE_USER_FIELDS = ["email", "login_id", "phone", "nickname"]