import fastapi

from app import config as app_config
from app.common import s3
from app.contents import schemas, service, store

router = fastapi.APIRouter()

_store: store.ContentsStore | None = None


def get_contents_store() -> store.ContentsStore:
    global _store

    if _store is None:
        config = app_config.get_config()
        _store = store.ContentsStore(
            s3_client=s3.create_s3_client(), bucket=config.s3_bucket
        )

    return _store


def get_contents_service() -> service.ContentsService:
    config = app_config.get_config()

    return service.ContentsService(
        contents_store=get_contents_store(),
        default_page_limit=config.default_widget_page_limit,
        default_workspace_id=config.default_workspace_id,
    )


@router.get("/murals/{mural_id}/widgets")
async def get_widgets(
    mural_id: str,
    contents_service: service.ContentsService = fastapi.Depends(get_contents_service),
    limit: int | None = None,
    next_token: str | None = fastapi.Query(default=None, alias="next"),
    widget_type: str | None = fastapi.Query(default=None, alias="type"),
    parent_id: str | None = fastapi.Query(default=None, alias="parentId"),
) -> schemas.WidgetsResponse:
    widgets, next_cursor = await contents_service.get_widgets(
        mural_id,
        limit=limit,
        cursor=next_token,
        widget_type=widget_type,
        parent_id=parent_id,
    )

    return schemas.WidgetsResponse(value=widgets, next=next_cursor)
