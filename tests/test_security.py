# tests/test_security.py
"""
Unit tests for the security core: hashing and JWT functions.

Run:
    pytest -q
"""

import time
from datetime import timedelta

import pytest

from app.core import security
from app.core.config import settings


def test_hash_and_verify_password_and_rehash_flag():
    plain = "very-secure-password-123!"
    hashed = security.hash_password(plain)
    assert isinstance(hashed, str) and len(hashed) > 0

    valid, should_rehash = security.verify_password(plain, hashed)
    assert valid is True
    # For a fresh bcrypt hash, passlib usually does not require an immediate rehash
    assert isinstance(should_rehash, bool)


def legacy_verify_example(plain, stored_hash):
    """
    Example legacy verification function used to simulate migrations.
    For test purposes, we will say that legacy 'hash' is just the plain string prefixed with "LEGACY:".
    """
    if stored_hash.startswith("LEGACY:"):
        return stored_hash == f"LEGACY:{plain}"
    return False


def test_verify_with_legacy_hash_triggers_rehash():
    plain = "old-password"
    legacy_stored = f"LEGACY:{plain}"

    valid, should_rehash = security.verify_password(plain, legacy_stored, legacy_verify=legacy_verify_example)
    assert valid is True
    # Because it matched legacy, we request rehash to update to bcrypt
    assert should_rehash is True


def test_create_and_decode_token():
    payload = {"sub": "alice@example.com", "user_id": 123}
    token = security.create_access_token(payload, expires_delta=timedelta(seconds=2))
    assert isinstance(token, str) and len(token) > 10

    data = security.decode_access_token(token)
    # The payload should include original claims plus exp/iat
    assert data["sub"] == "alice@example.com"
    assert data["user_id"] == 123
    assert "exp" in data and "iat" in data

    # Test expiry
    time.sleep(2.1)
    with pytest.raises(security.TokenDecodeError):
        security.decode_access_token(token)
