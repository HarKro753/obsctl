"""Pydantic request/response models."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response for GET /health."""

    status: str
    version: str


class UserInfo(BaseModel):
    """User info returned from Google OAuth."""

    google_id: str
    email: str
    name: str = ""


class TokenResponse(BaseModel):
    """Response containing a JWT token."""

    token: str


class CredentialsResponse(BaseModel):
    """Response for GET /credentials with CouchDB connection info."""

    couchdb_url: str
    couchdb_username: str
    couchdb_password: str


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
