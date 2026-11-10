import uuid
import time
from contextvars import ContextVar
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Scope, Receive, Send

correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id_ctx", default="")

class CorrelationIdMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        corr_id = None
        for name, value in scope.get("headers", []):
            if name.lower() == b"x-correlation-id":
                corr_id = value.decode("latin1")
                break
        if not corr_id:
            corr_id = str(uuid.uuid4())

        token = correlation_id_ctx.set(corr_id)
        start_time = time.time()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append("X-Correlation-ID", corr_id)
                headers.append("X-Process-Time", f"{time.time() - start_time:.4f}s")
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            correlation_id_ctx.reset(token)

def get_current_correlation_id() -> str:
    corr_id = correlation_id_ctx.get()
    return corr_id if corr_id else str(uuid.uuid4())
