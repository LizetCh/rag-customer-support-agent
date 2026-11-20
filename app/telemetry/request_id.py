"""Correlation IDs: one id per request, attached to every log line, to the
chat_logs row, and to the response, so a single request can be traced end to end.
"""

import logging
import re
import time
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from uuid import uuid4

from fastapi import Request, Response

HEADER = "X-Request-ID"

# The header comes from the client, so it is untrusted: accept only short, plain
# ids (UUIDs and most tracing formats fit). Anything else, such as a value with a
# newline that could forge a fake log line, is replaced with a fresh id.
_SAFE_ID = re.compile(r"[A-Za-z0-9._-]{1,64}")

# Each request (and each thread it hands work to) sees its own value.
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

logger = logging.getLogger(__name__)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def configure_logging() -> None:
    """Send the app's logs to stderr, each line tagged with its request id."""
    handler = logging.StreamHandler()
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s")
    )
    app_logger = logging.getLogger("app")
    app_logger.addHandler(handler)
    app_logger.setLevel(logging.INFO)


async def request_id_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    incoming = request.headers.get(HEADER, "")
    request_id = incoming if _SAFE_ID.fullmatch(incoming) else str(uuid4())
    token = request_id_var.set(request_id)
    started = time.perf_counter()
    try:
        response = await call_next(request)
        response.headers[HEADER] = request_id
        latency_ms = round((time.perf_counter() - started) * 1000)
        logger.info("%s %s -> %s in %d ms", request.method, request.url.path, response.status_code, latency_ms)
        return response
    finally:
        request_id_var.reset(token)
