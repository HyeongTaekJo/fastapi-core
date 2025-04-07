from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select
from post.model.model import PostModel

# 예를들어서 user, post의 모델이 서로 관계과 연동되어 있을 경우,
# 반드시 selectinload으로 불러와야 한다.
# 이유는 SQLAlchemy는 기본적으로 lazy-loading 이기 때문이다.
# lazy-loading -> 연관된 테이블의 데이터를 가져온다.
# 참고로 모델에 lazy="raise" 되어 있어서 반드시 selectinload을 통해서 관계를 설정해야 한다.


def get_default_post_query():
    return select(PostModel).options(
        selectinload(PostModel.user),
        # 필요시 추가: selectinload(PostModel.images),
    )