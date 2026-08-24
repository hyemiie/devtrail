"""
Central error taxonomy for the whole API.

Every provider adapter and service maps its own failure modes into ONE of
these so callers get a consistent error shape regardless of what went wrong
upstream. This is what "structured error taxonomy" means in the spec.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse


class APIError(Exception):
    """Base class every domain error inherits from."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    error_code: str = "bad_request"

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class InvalidInputError(APIError):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "invalid_input"


class ConsentNotGrantedError(APIError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "consent_not_granted"


class VerificationFailedError(APIError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "verification_failed"


class ProviderDownError(APIError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "provider_down"


class NotFoundError(APIError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"


class UnauthorizedError(APIError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "unauthorized"


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


def register_exception_handlers(app) -> None:
    app.add_exception_handler(APIError, api_error_handler)