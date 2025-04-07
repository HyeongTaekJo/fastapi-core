from fastapi import HTTPException, status

class AppException(HTTPException):
    def __init__(self, code: str, message: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "status_code": self.status_code
            }
        }

# 사용 예시:
# raise AppException(code="CUSTOM_ERROR", message="비즈니스 규칙 위반", status_code=400)


class NotFoundException(AppException):
    def __init__(self, target: str = "Resource"):
        super().__init__(
            code="NOT_FOUND",
            message=f"{target} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

# 사용 예시:
# raise NotFoundException("Post")
# raise NotFoundException("User")


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

# 사용 예시:
# raise UnauthorizedException()
# raise UnauthorizedException("Access token이 유효하지 않습니다.")


class ConflictException(AppException):
    def __init__(self, message: str = "Conflict occurred"):
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=status.HTTP_409_CONFLICT
        )

# 사용 예시:
# raise ConflictException("이미 존재하는 이메일입니다.")
# raise ConflictException("중복된 요청입니다.")
