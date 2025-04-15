import functools

def public(func):
    """
    NestJS의 @IsPublic()처럼 endpoint에 `_is_public` 메타데이터를 설정
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    setattr(wrapper, "_is_public", True)
    return wrapper
