"""JWT token issuance and verification."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

ALGORITHM = "HS256"
DEFAULT_EXPIRY_DAYS = 7


def issue_token(
    data: dict, secret: str, expires_days: int = DEFAULT_EXPIRY_DAYS
) -> str:
    """Create a signed JWT token.

    Args:
        data: Payload to encode in the token.
        secret: HMAC secret key.
        expires_days: Token lifetime in days.

    Returns:
        Encoded JWT string.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=expires_days)
    payload["exp"] = expire
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def verify_token(token: str, secret: str) -> dict:
    """Decode and verify a JWT token.

    Args:
        token: Encoded JWT string.
        secret: HMAC secret key used to sign the token.

    Returns:
        Decoded payload as a dict.

    Raises:
        JWTError: If the token is invalid, expired, or tampered with.
    """
    return jwt.decode(token, secret, algorithms=[ALGORITHM])
