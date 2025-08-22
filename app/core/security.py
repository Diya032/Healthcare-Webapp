# hash/verify pwd, create/decode JWT

# app/utils/security.py
"""
Security helpers:
- password hashing and verification (uses passlib CryptContext with bcrypt)
- optional "dual-verify" hook for legacy hashes (useful during migration)
- JWT creation and decoding using PyJWT

Design notes:
- Keep this file as the single place that deals with credential hashing and tokens.
- When migrating from a legacy hash, pass a `legacy_verify` callable to `verify_password`.
  If the legacy verification succeeds, callers may choose to re-hash the password with the new scheme.
"""

import datetime
from datetime import timedelta
from typing import Callable, Optional, Tuple, Dict, Any

from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext


from .config import settings

# Configure passlib to use bcrypt as the preferred hashing algorithm.
# bcrypt is secure and widely supported.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ----------------------------
# Password helpers
# ----------------------------
def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password for storage.

    :param plain_password: password from user input
    :return: hashed password (bcrypt)
    """
    return pwd_context.hash(plain_password)


def verify_password(
    plain_password: str,
    stored_hash: str,
    legacy_verify: Optional[Callable[[str, str], bool]] = None
) -> Tuple[bool, bool]:
    """
    Verify a plaintext password against the stored hash.

    Dual-verify support:
      - First attempts to verify with the current scheme (passlib/bcrypt).
      - If that fails and `legacy_verify` is provided, calls `legacy_verify(plain_password, stored_hash)`.
        If legacy_verify returns True, returns (True, True) indicating verification success
        and that the stored hash should be re-hashed with the current scheme.
      - Otherwise returns (False, False).

    :param plain_password: user-supplied password (plaintext)
    :param stored_hash: hash stored in DB (could be bcrypt or legacy)
    :param legacy_verify: optional callable to verify legacy hashes. Signature: (plain, stored_hash) -> bool
    :returns: (is_valid: bool, should_rehash_with_current_scheme: bool)
    """
    # 1) Try current (bcrypt via passlib)
    try:
        valid = pwd_context.verify(plain_password, stored_hash)
    except Exception:
        # If passlib throws, treat as failure and fall through to legacy_verify (if provided)
        valid = False

    if valid:
        # If the hash is valid but is using an older algorithm parameters, we can indicate rehash.
        # This allows callers to re-hash the password transparently on next successful login.
        should_rehash = pwd_context.needs_update(stored_hash)
        return True, should_rehash

    # 2) Try legacy verification if supplied
    if legacy_verify is not None:
        try:
            legacy_ok = legacy_verify(plain_password, stored_hash)
        except Exception:
            legacy_ok = False

        if legacy_ok:
            # Indicates the legacy hash matched — caller should re-hash using `hash_password` and persist.
            return True, True

    # 3) No match
    return False, False


# ----------------------------
# JWT helpers
# ----------------------------
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token.

    :param data: dictionary of claims to include in the token payload (e.g. {"sub": email, "user_id": id})
                 NOTE: we don't mutate the `data` dict in-place; we copy.
    :param expires_delta: optional timedelta to override the default TTL from settings
    :return: JWT (string)
    """
    to_encode = data.copy()

     # Make sure sub is string
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    now = datetime.datetime.now(datetime.timezone.utc)
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = now + expires_delta

    # Standard claims
    to_encode.update({
        "exp": expire,
        "iat": now,
    })

    # Optional issuer/audience if provided in settings (helps when moving to B2C)
    if settings.JWT_ISSUER:
        to_encode["iss"] = settings.JWT_ISSUER
    if settings.JWT_AUDIENCE:
        to_encode["aud"] = settings.JWT_AUDIENCE

    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    # PyJWT returns a str for encode on modern versions
    return token


class TokenDecodeError(Exception):
    """Raised when token decoding/validation fails. Wraps PyJWT exceptions if needed."""
    pass


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT.

    Verifies signature, expiry, and optional audience/issuer if configured in settings.

    :param token: JWT string
    :return: payload dict
    :raises TokenDecodeError: on validation failure (expired, invalid signature, bad claims)
    """
    options = {"verify_aud": bool(settings.JWT_AUDIENCE)}
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.JWT_AUDIENCE if settings.JWT_AUDIENCE else None,
            issuer=settings.JWT_ISSUER if settings.JWT_ISSUER else None,
            options=options,
        )
    except ExpiredSignatureError as exc:
        raise TokenDecodeError("token expired") from exc
    except JWTError as exc:
        raise TokenDecodeError("invalid token or claims") from exc

    return payload
