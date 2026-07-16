import datetime
import secrets

import jwt

from app.auth import schemas

_SIGNING_KEY = "mural-api-stub-fake-oauth-signing-key"
_ALGORITHM = "HS256"


class AuthService:
    """Issues stub OAuth2 tokens. Does not validate credentials.

    ``access_token`` is a JWT because the MCP client decodes it (with
    signature verification disabled) to read its ``exp`` claim.
    """

    def __init__(self, expires_in: int) -> None:
        self._expires_in = expires_in

    def issue_token(self) -> schemas.TokenResponse:
        now = datetime.datetime.now(datetime.UTC)
        access_token = jwt.encode(
            {
                "iat": now,
                "exp": now + datetime.timedelta(seconds=self._expires_in),
                "jti": secrets.token_urlsafe(16),
            },
            _SIGNING_KEY,
            algorithm=_ALGORITHM,
        )

        return schemas.TokenResponse(
            access_token=access_token,
            refresh_token=secrets.token_urlsafe(32),
            expires_in=self._expires_in,
        )
