from typing import Any

from app.murals import errors, store


class MuralService:
    """Application service for reading a single mural."""

    def __init__(
        self,
        mural_store: store.MuralStore,
        default_workspace_id: str | None,
    ) -> None:
        self._store = mural_store
        self._default_workspace_id = default_workspace_id

    async def get_mural(self, mural_id: str) -> dict[str, Any]:
        parsed_id = store.MuralId.parse(mural_id, self._default_workspace_id)
        board = await self._store.get_board(parsed_id)

        if board is None:
            raise errors.MuralNotFoundError(mural_id)

        return board
