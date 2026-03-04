"""Credentials route — returns CouchDB connection info for authenticated users."""

from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.config import Settings
from app.db.queries import get_credentials
from app.models.schemas import CredentialsResponse
from app.services.jwt import verify_token

router = APIRouter()
security = HTTPBearer()


def _get_settings(request: Request) -> Settings:
    return request.app.state.settings


def _get_db(request: Request) -> sqlite3.Connection:
    return request.app.state.db


@router.get("/credentials", response_model=CredentialsResponse)
async def credentials(
    request: Request,
    auth: HTTPAuthorizationCredentials = Depends(security),
    settings: Settings = Depends(_get_settings),
    db: sqlite3.Connection = Depends(_get_db),
) -> CredentialsResponse:
    """Return CouchDB credentials for the authenticated user.

    Requires a valid JWT in the Authorization header.
    Returns 401 for missing/invalid/expired tokens, 404 if vault not provisioned.
    """
    try:
        payload = verify_token(auth.credentials, settings.jwt_secret)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    creds = get_credentials(db, user_id)
    if creds is None:
        raise HTTPException(status_code=404, detail="Vault not provisioned")

    return CredentialsResponse(
        couchdb_url=creds["couchdb_url"],
        couchdb_username=creds["couchdb_username"],
        couchdb_password=creds["couchdb_password"],
    )
