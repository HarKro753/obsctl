"""Tests for the JWT service."""

from datetime import datetime, timedelta, timezone

import pytest
from jose import JWTError, jwt

from app.services.jwt import ALGORITHM, issue_token, verify_token

SECRET = "test-secret-key"


def test_issue_token_returns_string():
    """issue_token should return a non-empty string."""
    token = issue_token({"user_id": 1}, SECRET)
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token_roundtrip():
    """Payload data should survive encode/decode roundtrip."""
    payload = {"user_id": 42, "email": "test@example.com"}
    token = issue_token(payload, SECRET)
    decoded = verify_token(token, SECRET)
    assert decoded["user_id"] == 42
    assert decoded["email"] == "test@example.com"


def test_verify_token_wrong_secret():
    """verify_token should raise JWTError with wrong secret."""
    token = issue_token({"user_id": 1}, SECRET)
    with pytest.raises(JWTError):
        verify_token(token, "wrong-secret")


def test_verify_token_malformed():
    """verify_token should raise JWTError for malformed tokens."""
    with pytest.raises(JWTError):
        verify_token("not-a-real-token", SECRET)


def test_verify_token_expired():
    """verify_token should raise JWTError for expired tokens."""
    # Create a token that expired 1 second ago
    payload = {
        "user_id": 1,
        "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    with pytest.raises(JWTError):
        verify_token(token, SECRET)


def test_payload_contains_exp():
    """Issued tokens should contain an exp claim."""
    token = issue_token({"user_id": 1}, SECRET)
    decoded = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    assert "exp" in decoded
    # Expiry should be in the future
    exp = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
    assert exp > datetime.now(timezone.utc)
