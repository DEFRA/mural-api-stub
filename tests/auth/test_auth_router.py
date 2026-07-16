import fastapi.testclient

import app.entrypoints.fastapi

client = fastapi.testclient.TestClient(app.entrypoints.fastapi.app)

TOKEN_URL = "/api/public/v1/authorization/oauth2/token"


class TestTokenEndpoint:
    """Test the fake OAuth2 token endpoint used by the MCP server."""

    def test_authorization_code_grant_form_encoded(self):
        response = client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": "client",
                "client_secret": "secret",
                "code": "abc",
                "redirect_uri": "http://localhost/cb",
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["access_token"]
        assert body["refresh_token"]
        assert body["token_type"] == "bearer"
        assert body["expires_in"] == 900

    def test_refresh_token_grant_json(self):
        response = client.post(
            TOKEN_URL,
            json={"grant_type": "refresh_token", "refresh_token": "old"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["access_token"]
        assert body["refresh_token"]
        assert body["token_type"] == "bearer"
        assert body["expires_in"] == 900

    def test_tokens_are_fresh_each_call(self):
        first = client.post(
            TOKEN_URL, json={"grant_type": "refresh_token", "refresh_token": "old"}
        ).json()
        second = client.post(
            TOKEN_URL, json={"grant_type": "refresh_token", "refresh_token": "old"}
        ).json()

        assert first["access_token"] != second["access_token"]
        assert first["refresh_token"] != second["refresh_token"]

    def test_unsupported_grant_type(self):
        response = client.post(TOKEN_URL, json={"grant_type": "client_credentials"})

        assert response.status_code == 400
        assert response.json()["error"] == "unsupported_grant_type"

    def test_missing_grant_type(self):
        response = client.post(TOKEN_URL, json={})

        assert response.status_code == 400
        assert response.json()["error"] == "unsupported_grant_type"
