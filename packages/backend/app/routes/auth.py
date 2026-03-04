"""Google OAuth authentication routes."""

from __future__ import annotations

import secrets
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.config import Settings
from app.db.queries import save_credentials, upsert_user
from app.models.schemas import TokenResponse
from app.services.couchdb import provision_vault
from app.services.jwt import issue_token
from app.services.oauth import exchange_code, google_auth_url

router = APIRouter(prefix="/auth")


def _get_settings(request: Request) -> Settings:
    return request.app.state.settings


def _get_db(request: Request) -> sqlite3.Connection:
    return request.app.state.db


@router.get("/google")
async def auth_google(settings: Settings = Depends(_get_settings)) -> RedirectResponse:
    """Redirect user to Google OAuth consent screen."""
    state = secrets.token_urlsafe(32)
    url = google_auth_url(settings, state)
    return RedirectResponse(url=url, status_code=302)


@router.get("/callback", response_model=TokenResponse)
async def auth_callback(
    code: str,
    state: str = "",
    settings: Settings = Depends(_get_settings),
    db: sqlite3.Connection = Depends(_get_db),
) -> TokenResponse:
    """Handle Google OAuth callback.

    Exchanges the authorization code for user info, upserts the user,
    provisions a CouchDB vault (idempotent), and returns a JWT.
    """
    try:
        user_info = await exchange_code(settings, code)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"OAuth exchange failed: {exc}")

    # Upsert user in local DB
    user = upsert_user(db, user_info.google_id, user_info.email)

    # Provision CouchDB vault (idempotent)
    try:
        vault = await provision_vault(settings, user["id"])
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Vault provisioning failed: {exc}")

    # Save credentials
    save_credentials(
        db,
        user["id"],
        vault["url"],
        vault["username"],
        vault["password"],
    )

    # Issue JWT
    token = issue_token(
        {"user_id": user["id"], "email": user_info.email},
        settings.jwt_secret,
    )

    return TokenResponse(token=token)
