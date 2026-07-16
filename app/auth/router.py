from typing import Any

import fastapi

from app import config as app_config
from app.auth import schemas, service

router = fastapi.APIRouter()

_SUPPORTED_GRANTS = {"authorization_code", "refresh_token"}


def get_auth_service() -> service.AuthService:
    config = app_config.get_config()

    return service.AuthService(expires_in=config.stub_token_expires_in)


async def _read_params(request: fastapi.Request) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        body: dict[str, Any] = await request.json()
        return body

    form = await request.form()
    return dict(form)


@router.post("/authorization/oauth2/token", response_model=None)
async def issue_token(
    request: fastapi.Request,
    auth_service: service.AuthService = fastapi.Depends(get_auth_service),
) -> schemas.TokenResponse | fastapi.responses.JSONResponse:
    params = await _read_params(request)
    grant_type = params.get("grant_type")

    if grant_type not in _SUPPORTED_GRANTS:
        return fastapi.responses.JSONResponse(
            status_code=400,
            content={
                "error": "unsupported_grant_type",
                "error_description": f"Unsupported grant_type: {grant_type!r}",
            },
        )

    return auth_service.issue_token()
