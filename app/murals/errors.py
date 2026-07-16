from app.common import errors


class MuralNotFoundError(errors.ApiError):
    """A mural (or its stored data) could not be located."""

    status_code = 404
    code = "MURAL_NOT_FOUND"

    def __init__(self, mural_id: str) -> None:
        super().__init__(f"Mural not found: {mural_id}")
        self.mural_id = mural_id
