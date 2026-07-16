from typing import Any

from app.contents import errors, pagination, store
from app.murals import store as mural_store


class ContentsService:
    """Application service for reading a mural's widgets."""

    def __init__(
        self,
        contents_store: store.ContentsStore,
        default_page_limit: int,
        default_workspace_id: str | None,
    ) -> None:
        self._store = contents_store
        self._default_page_limit = default_page_limit
        self._default_workspace_id = default_workspace_id

    async def get_widgets(
        self,
        mural_id: str,
        limit: int | None,
        cursor: str | None,
        widget_type: str | None,
        parent_id: str | None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        if limit is not None and limit <= 0:
            raise errors.LimitInvalidError(limit)

        try:
            offset = pagination.decode_cursor(cursor)
        except ValueError as exc:
            raise errors.PaginationInvalidError(str(exc)) from exc

        parsed_id = mural_store.MuralId.parse(mural_id, self._default_workspace_id)
        widgets = await self._store.get_widgets(parsed_id)

        if widgets is None:
            raise errors.MuralNotFoundError(mural_id)

        widgets = self._filter(widgets, widget_type, parent_id)
        effective_limit = limit or self._default_page_limit
        page = widgets[offset : offset + effective_limit]

        next_token = None
        if offset + effective_limit < len(widgets):
            next_token = pagination.encode_cursor(offset + effective_limit)

        return page, next_token

    @staticmethod
    def _filter(
        widgets: list[dict[str, Any]],
        widget_type: str | None,
        parent_id: str | None,
    ) -> list[dict[str, Any]]:
        if widget_type:
            types = {t.strip() for t in widget_type.split(",") if t.strip()}
            widgets = [w for w in widgets if w.get("type") in types]

        if parent_id:
            widgets = [w for w in widgets if w.get("parentId") == parent_id]

        return widgets
