from contextvars import ContextVar

from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)
from starlette.requests import Request

CLIENT_IP_CTX_KEY = "client_ip"

_client_ip_ctx_var: ContextVar = ContextVar(
    CLIENT_IP_CTX_KEY, default=None
)


def get_client_ip() -> str:
    return _client_ip_ctx_var.get()


class RequestContextMiddleware(BaseHTTPMiddleware):

    """ The middleware for processing requests. Gets the IP address of the
    client from the request. """

    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ):
        client_ip = _client_ip_ctx_var.set(request.client.host)
        response = await call_next(request)
        _client_ip_ctx_var.reset(client_ip)

        return response
