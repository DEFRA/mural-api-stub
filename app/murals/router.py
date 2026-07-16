import fastapi

from app import config as app_config
from app.common import s3
from app.murals import schemas, service, store

router = fastapi.APIRouter()

_store: store.MuralStore | None = None


def get_mural_store() -> store.MuralStore:
    global _store

    if _store is None:
        config = app_config.get_config()
        _store = store.MuralStore(
            s3_client=s3.create_s3_client(), bucket=config.s3_bucket
        )

    return _store


def get_mural_service() -> service.MuralService:
    config = app_config.get_config()

    return service.MuralService(
        mural_store=get_mural_store(),
        default_workspace_id=config.default_workspace_id,
    )


@router.get("/murals/{mural_id}")
async def get_mural(
    mural_id: str,
    mural_service: service.MuralService = fastapi.Depends(get_mural_service),
) -> schemas.MuralResponse:
    value = await mural_service.get_mural(mural_id)

    return schemas.MuralResponse(value=value)
