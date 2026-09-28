"""HTTP request logging and global error handling middleware."""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs incoming HTTP requests, timing, status codes, and exceptions."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Exclude noisy polling / static routes from debug logs if desired
            if not request.url.path.startswith("/static"):
                logger.log_api_request(
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    client_ip=client_ip,
                )

            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            return response
        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            logger.exception(
                f"Unhandled HTTP Exception processing {request.method} {request.url.path}",
                error=str(exc),
                duration_ms=duration_ms,
                client_ip=client_ip,
            )
            raise exc
