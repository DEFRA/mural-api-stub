"""Mural-compatible error responses.

Errors are rendered as Mural's standard envelope, ``{"code": ..., "message": ...}``,
matching https://developers.mural.co/public/docs/error-codes so stub clients see the
same shape the real API returns.
"""

import fastapi
import pydantic


class ErrorResponse(pydantic.BaseModel):
    """Mural's standard error envelope."""

    code: str
    message: str


class ApiError(Exception):
    """Base for errors that render as a Mural ``{code, message}`` response.

    Subclasses set ``status_code`` and ``code``; the message is per-instance.
    """

    status_code: int = 500
    code: str = "INTERNAL_SERVER_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


async def api_error_handler(
    _: fastapi.Request, exc: Exception
) -> fastapi.responses.JSONResponse:
    error = exc if isinstance(exc, ApiError) else ApiError(str(exc))

    return fastapi.responses.JSONResponse(
        status_code=error.status_code,
        content=ErrorResponse(code=error.code, message=error.message).model_dump(),
    )
