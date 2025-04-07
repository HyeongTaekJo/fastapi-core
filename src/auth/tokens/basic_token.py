from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from auth.service import AuthService

security = HTTPBasic()
# ★ HTTPBasic이 자동으로 검증해주는 것들 ★
# Authorization가 존재하는지?
# Authorization 헤더 값이 Basic <Base64> 형식인지?
# Base64(username:password)가 올바르게 디코딩되는지?
# username과 password 값이 있는지?

async def basic_token(
    credentials: HTTPBasicCredentials = Depends(security), 
    auth_service: AuthService = Depends(AuthService)
):
    """ Basic Auth를 사용한 인증 """
     # credentials가 None인지 확인
    if not credentials:
        raise HTTPException(status_code=401, detail="Basic 인증 정보가 제공되지 않았습니다.")
    
    user = await auth_service.authenticate_with_email_password(
        email=credentials.username, # credentials의 username은 필드 이름일 뿐이고, 실제 값은 이메일일 수도 있고 아이디일 수도 있다.
        password=credentials.password
    )

    if not user:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    return user


""" 아래는 HTTPBasicCredentials을 사용하지 않고 내가 직접 만든 로직 """
# from fastapi import Depends, HTTPException, Header
# from auth.service import AuthService

# async def BasicToken(
#     authorization: str = Header(None),  # Authorization 헤더 받기
#     auth_service: AuthService = Depends(AuthService)
# ):
#     """ Basic Token을 검증하는 의존성 함수 """

#     if not authorization:
#         raise HTTPException(status_code=401, detail="토큰이 없습니다.") # 클라이언트에서 Basic Token을 안보냄

#     token = auth_service.extract_token(authorization, is_bearer=False)  # Basic Token 추출(basic 이라서 is_bearer=False)
#     credentials = auth_service.decode_basic_token(token)  # Base64 디코딩

#     #  이메일과 비밀번호로 사용자 인증
#     user = await auth_service.authenticate_with_email_password(
#         email=credentials["email"],
#         password=credentials["password"],
#     )

#     return user  # 인증된 사용자 반환