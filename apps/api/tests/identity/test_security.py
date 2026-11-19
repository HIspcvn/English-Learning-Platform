import re

import pytest
from argon2 import PasswordHasher
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.identity.schemas import EmailRequest, VerificationRequest
from app.identity.service import digest_token, hash_password, new_token
from app.main import app


def test_email_preserves_alias_and_normalizes_domain():
    email = EmailRequest(email="  Le.Arner+tag@EXAMPLE.COM ").email

    assert email == "Le.Arner+tag@example.com"
    assert EmailRequest(email="a@bücher.example").email == "a@xn--bcher-kva.example"


@pytest.mark.parametrize("email", ["learner", "name <a@example.com>", "a@localhost", "x" * 255])
def test_bad_email(email):
    with pytest.raises(ValidationError):
        EmailRequest(email=email)


@pytest.mark.parametrize("password", ["x" * 11, "x" * 129])
def test_password_length_bounds(password):
    with pytest.raises(ValidationError):
        VerificationRequest(token="invalid", password=password, display_name="Learner")


@pytest.mark.parametrize("field", ["token", "password", "display_name"])
def test_invalid_unicode_is_rejected_before_credentials_are_processed(field):
    values = {"token": "invalid", "password": "synthetic password", "display_name": "Learner"}
    values[field] += "\ud800"
    with pytest.raises(ValidationError) as rejected:
        VerificationRequest(**values)
    assert rejected.value.errors(include_input=False)[0]["loc"] == (field,)


def test_password_hash_uses_argon2id_and_preserves_whitespace():
    password = "  synthetic fixture  "
    encoded = hash_password(password)

    assert encoded.startswith("$argon2id$")
    assert PasswordHasher().verify(encoded, password)
    assert hash_password(password) != encoded


def test_token_randomness_and_digest():
    first = new_token()
    second = new_token()

    assert re.fullmatch(r"[0-9A-Za-z_-]{43}", first)
    assert first != second
    assert digest_token(first) == digest_token(first)
    assert len(digest_token(first)) == 32
    assert digest_token(first) != digest_token(second)


def test_secure_guest_cookie_and_safe_database_outage(monkeypatch):
    origin = "https://learn.example.com"
    monkeypatch.setenv("AUTH_PUBLIC_ORIGIN", origin)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:outage-sentinel@127.0.0.1:1/db")
    with TestClient(app, base_url=origin) as client:
        bootstrap = client.get("/api/v1/auth/session")
        cookie = bootstrap.headers["set-cookie"]
        assert cookie.startswith("__Host-elp_guest_csrf=")
        assert all(
            attribute in cookie for attribute in ("HttpOnly", "Path=/", "Secure", "SameSite=lax")
        )
        assert "Domain=" not in cookie
        assert bootstrap.headers["cache-control"] == "private, no-store"

        response = client.post(
            "/api/v1/auth/verify",
            headers={"Origin": origin, "X-CSRF-Token": bootstrap.json()["csrf_token"]},
            json={"token": "unknown", "password": "synthetic password", "display_name": "Learner"},
        )

    assert response.status_code == 503
    assert int(response.headers["retry-after"]) > 0
    assert response.headers["content-type"] == "application/problem+json"
    assert "outage-sentinel" not in response.text
