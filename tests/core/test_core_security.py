from datetime import datetime, timedelta, UTC

import pytest
from jose import jwt

from app.core.config import get_settings
from app.core.security import create_access_token, decode_token, hash_password, verify_password


def test_hash_and_verify_password():
    hashed = hash_password("pw-123")
    assert verify_password("pw-123", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_create_and_decode_token_roundtrip():
    token = create_access_token({"sub": 123}, token_version=7)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "123"
    assert payload["ver"] == 7
    assert payload["type"] == "access"
    assert isinstance(payload["iat"], int)
    assert isinstance(payload["exp"], int)


def test_create_access_token_requires_sub():
    with pytest.raises(ValueError):
        create_access_token({"sub": None}, token_version=1)


def test_decode_token_invalid_returns_none():
    assert decode_token("not-a-jwt") is None


def test_decode_token_missing_sub_returns_none():
    settings = get_settings().secret
    now = datetime.now(UTC)
    payload = {
        "exp": int((now + timedelta(minutes=5)).timestamp()),
        "iat": int(now.timestamp()),
        "type": "access",
        "ver": 1,
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    assert decode_token(token) is None
