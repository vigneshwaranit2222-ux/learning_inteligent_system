import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_token

def test_password_hashing():
    raw_pass = "StrongSecret123!"
    h = hash_password(raw_pass)
    assert h != raw_pass
    assert verify_password(raw_pass, h) is True
    assert verify_password("WrongPass", h) is False

def test_jwt_generation_and_decoding():
    user_id = "test-user-12345"
    role = "learner"
    token = create_access_token(user_id, role)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["role"] == role
    assert payload["type"] == "access"

def test_invalid_jwt_rejection():
    assert decode_token("invalid.token.structure") is None
