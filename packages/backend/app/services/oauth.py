"""Google OAuth 2.0 flow using authlib."""

from __future__ import annotations

from urllib.parse import urlencode

import httpx

from app.config import Settings
from app.models.schemas import UserInfo

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"

SCOPES = "openid email profile"


def google_auth_url(settings: Settings, state: str) -> str:
    """Build the Google OAuth authorization redirect URL.

    Args:
        settings: Application settings with client ID and redirect URI.
        state: CSRF state parameter.

    Returns:
        Full authorization URL string.
    """
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(params)}"


async def exchange_code(settings: Settings, code: str) -> UserInfo:
    """Exchange an authorization code for user info.

    Args:
        settings: Application settings with client credentials.
        code: Authorization code from Google callback.

    Returns:
        UserInfo with google_id, email, and name.

    Raises:
        httpx.HTTPStatusError: If token exchange or userinfo request fails.
    """
    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        token_resp = await client.post(
            GOOGLE_TOKEN_ENDPOINT,
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.google_redirect_uri,
            },
        )
        token_resp.raise_for_status()
        access_token = token_resp.json()["access_token"]

        # Fetch user info
        userinfo_resp = await client.get(
            GOOGLE_USERINFO_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        userinfo_resp.raise_for_status()
        data = userinfo_resp.json()

    return UserInfo(
        google_id=data["sub"],
        email=data["email"],
        name=data.get("name", ""),
    )
