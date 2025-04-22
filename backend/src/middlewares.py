import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.requests import Request
from loguru import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app,
    ):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request.state.session_id = str(uuid.uuid4())
        logger.debug(f"{request.state.session_id} - OPENED: {request.method} {request.url.components.path}")
        response = await call_next(request)
        log = (f"{request.state.session_id} - CLOSED: "
               f"{request.method} {request.url.components.path} "
               f"{response.status_code}")
        if 500 <= response.status_code < 600:
            logger.error(log)
            logger.error("MORE INFO:")
            logger.error(request.state.session_id, repr(request))
            logger.error(request.state.session_id, repr(response))
        else:
            logger.info(log)
        return response
