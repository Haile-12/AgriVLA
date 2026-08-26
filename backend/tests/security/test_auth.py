"""
Security tests for JWT and authentication.
"""
import pytest
from app.auth.jwt import create_access_token, decode_access_token
from app.auth.password import get_password_hash, verify_password

class TestPasswordHashing:
    def test_hash_and_verify(self):
        hashed = get_password_hash("securepassword123")
        assert hashed != "securepassword123"
        assert verify_password("securepassword123", hashed) is True

    def test_wrong_password_fails(self):
        hashed = get_password_hash("correctpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_hash_is_unique(self):
        h1 = get_password_hash("same_password")
        h2 = get_password_hash("same_password")
        assert h1 != h2  # Argon2 uses random salt

class TestJWT:
    def test_create_and_decode_token(self):
        token = create_access_token(data={"sub": "user123", "tid": "tok456"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["tid"] == "tok456"

    def test_tampered_token_rejected(self):
        token = create_access_token(data={"sub": "user123", "tid": "tok456"})
        tampered = token[:-5] + "XXXXX"
        payload = decode_access_token(tampered)
        assert payload is None

    def test_empty_token_rejected(self):
        assert decode_access_token("") is None

    def test_garbage_token_rejected(self):
        assert decode_access_token("not.a.jwt.token") is None
