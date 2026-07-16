import pydantic


class TokenResponse(pydantic.BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105
    expires_in: int
