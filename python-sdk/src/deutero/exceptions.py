"""Exceptions raised by the Deutero Python SDK."""

from __future__ import annotations

from typing import Any, Optional


class DeuteroError(Exception):
    """Base exception for all Deutero SDK errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class APIError(DeuteroError):
    """An error returned by the Deutero API.

    Attributes:
        status_code: HTTP status code of the response.
        body: Parsed response body, if available.
        request_id: Request ID from headers, if available.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        body: Optional[Any] = None,
        request_id: Optional[str] = None,
    ) -> None:
        self.status_code = status_code
        self.body = body
        self.request_id = request_id
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(status_code={self.status_code}, message={self.message!r})"


class AuthenticationError(APIError):
    """Raised when the API key is invalid or missing (HTTP 401/403)."""


class NotFoundError(APIError):
    """Raised when a requested resource is not found (HTTP 404)."""


class ValidationError(APIError):
    """Raised when the request fails validation (HTTP 400/422)."""


class RateLimitError(APIError):
    """Raised when rate limits are exceeded (HTTP 429)."""


class InsufficientCreditsError(APIError):
    """Raised when the account lacks credits for the operation (HTTP 402)."""


class InternalServerError(APIError):
    """Raised for server-side errors (HTTP 5xx)."""


class BadGatewayError(APIError):
    """Raised when an upstream service fails (HTTP 502)."""


class ConnectionError(DeuteroError):
    """Raised when a network connection cannot be established."""


class TimeoutError(DeuteroError):
    """Raised when a request times out."""


_STATUS_MAP: dict[int, type[APIError]] = {
    400: ValidationError,
    401: AuthenticationError,
    402: InsufficientCreditsError,
    403: AuthenticationError,
    404: NotFoundError,
    422: ValidationError,
    429: RateLimitError,
    502: BadGatewayError,
}


def raise_for_status(status_code: int, body: Any, request_id: Optional[str] = None) -> None:
    """Raise an appropriate exception based on the HTTP status code."""
    if 200 <= status_code < 300:
        return

    detail = ""
    if isinstance(body, dict):
        detail = body.get("detail", body.get("message", ""))
    elif isinstance(body, str):
        detail = body

    message = f"HTTP {status_code}: {detail}" if detail else f"HTTP {status_code}"

    exc_class = _STATUS_MAP.get(status_code)
    if exc_class is None:
        if status_code >= 500:
            exc_class = InternalServerError
        else:
            exc_class = APIError

    raise exc_class(message, status_code=status_code, body=body, request_id=request_id)
