from app.common import errors
from app.murals.errors import MuralNotFoundError

__all__ = ["LimitInvalidError", "MuralNotFoundError", "PaginationInvalidError"]


class PaginationInvalidError(errors.ApiError):
    """The ``next`` pagination token is malformed."""

    status_code = 400
    code = "PAGINATION_INVALID"


class LimitInvalidError(errors.ApiError):
    """The ``limit`` query parameter is out of range."""

    status_code = 400
    code = "LIMIT_INVALID"

    def __init__(self, limit: int | None) -> None:
        super().__init__(f"Invalid limit: {limit}")
        self.limit = limit
