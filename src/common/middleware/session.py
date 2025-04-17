from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response, FastAPI
import uuid, json, logging
from cache.redis_context import get_redis_from_context

class RedisSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, session_cookie: str = "session_redis_id", max_age: int = 3600):
        super().__init__(app)
        self.session_cookie = session_cookie
        self.max_age = max_age

    # 상세정보는 redis에 들어가는 것을 여기서 구현하는 것
    async def dispatch(self, request: Request, call_next):
        redis = get_redis_from_context()

        response = None
        # session_id cookie key로 session_id(redis의 key)값을 가져옴. 
        session_id = request.cookies.get(self.session_cookie)
        # 신규 session인지 구분. 
        initial_session_was_empty = True
        # 만약 cookie에 session_id 값이 있으면
        if self.max_age is None or self.max_age <= 0: # max_age에는 0보다 작거나 None을 넣으면 안된다.
            response = await call_next(request)
            return response
        try:
            if session_id:
                # redis에서 해당 session_id값으로 저장된 개별 session_data를 가져옴
                session_data = await redis.hgetall(f"session:{session_id}")
                # redis에 해당 session_id값으로 데이터가 없을 수도 있음. 만약 있다면
                if session_data:
                    # fastapi의 request.state 객체에 새롭게 session 객체를 만들고, 여기에 session data를 저장. 
                    request.state.session = {k: json.loads(v) for k, v in session_data.items()} # session_data에는 id, name 등등 실제값이 json형태로 있는 것을 dict 형태로 바꿔서 redis에 넣는다.
                    await redis.expire(f"session:{session_id}", self.max_age) # 기존에 expire가 설정되어 있으면 신규로 설정한다 즉, 접근할 때마다 신규로 업데이트된다.
                    initial_session_was_empty = False
                # 만약 없다면, redis에서 여러 이유로 데이터가 삭제되었음. 
                # request.state.session 객체도 초기화 시키고, 신규 session으로 간주
                else:
                    request.state.session = {}
                    # session_id cookie를 가지고 있지 않다면, 이는 신규 session이고, 추후에 response에 set_cookie 호출. 
                    # new_session = True
            # cookie에 session_id 값이 없다면. 
            else:
                # 새로운 session_id값을 uuid로 생성하고 request.state.session값을 초기화.
                # 신규 session으로 간주.  
                session_id = str(uuid.uuid4())
                request.state.session = {}
                # new_session = True

            # FastAPI의 미들웨어에서 요청을 다음 미들웨어 또는 최종 API 핸들러로 전달
            # 최종 API 핸들러로 간다는 것은 로그인하면 @router.post("/login") 여기를 타는데 
            # response = await call_next(request) 이렇게하면 @router.post("/login") 함수로 넘어가서 
            # 함수를 실행하고 다시 돌아온다는 뜻이다.
            response = await call_next(request) 
            if request.state.session:
                # logging.info("##### request.state.session:" + str(request.state.session))
                # 초기 접속은 물론, 지속적으로 접속하면 max_age를 계속 갱신. 
                response.set_cookie(self.session_cookie, session_id, max_age=self.max_age, httponly=True)
                # redis에서 해당 session_id를 가지는 값을 hash로 저장. 
                # request.state.session값의 변경 여부와 관계없이 저장
                # expiration time을 지속적으로 max_age로 갱신.
                for field, value in request.state.session.items():
                    await redis.hset(f"session:{session_id}", field, json.dumps(value))
                await redis.expire(f"session:{session_id}", self.max_age)

                #########################################
                # 만일 로그아웃을 했을 때, 해당 session_id로 설정된 redis의 데이터는 남아있다
                # 이유는 여기에는 redis의 데이터를 지우는게 없으니까
                # 하지만 redis에 만료 기간을 설정해뒀기 때문에 안해도 되고, 로그아웃했을 때 삭제하는 로직을 추가해도 된다.
                # 보통은 그냥 냅둔다.
                ############################################

                ###############################################
                # 서버가 내려가면 redis도 모두 내려가는게 맞다
                # 하지만 여기에는 로직이 없으므로 추후에 추가할 것
                # lifespan에 적용하면 된다.
                #################################################

            else:
                # request.state.session가 비어있는데, initial_session_was_empty가 False라는 것은
                # fastapi API 로직에서 request.state.session이 clear() 호출되어서 삭제되었음을 의미. 
                # logout이므로 redis에서 해당 session_id 값을 삭제하고, 브라우저의 cookie도 삭제. 
                if not initial_session_was_empty:
                    # logging.info("##### redis value before deletion:" + str(redis_client.get(session_id)))
                    await redis.delete(f"session:{session_id}")
                    # logging.info("##### redis value after deletion:" + str(redis_client.get(session_id)))
                    response.delete_cookie(self.session_cookie)

        except Exception as e:
            logging.critical("error in redis session middleware:" + str(e))
        
        return response
