import re
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.identity.models import LearningPreferences
from app.identity.service import digest_token

from .helpers import (
    AUTH,
    ORIGIN,
    PASSWORD,
    SESSION_COOKIE,
    assert_problem,
    login,
    replay_cookie,
    session_view,
)

EMAIL = "learner@example.com"
pytestmark = pytest.mark.integration


def test_authenticated_session_contains_user_view_and_stores_only_cookie_digest(
    browser_factory, create_user, identity_engine
):
    user_id = create_user(EMAIL, "Học viên")
    client = browser_factory()

    response = login(client, EMAIL.upper())

    assert response.status_code == 200
    assert response.headers["cache-control"] == "private, no-store"
    cookie = next(
        value
        for value in response.headers.get_list("set-cookie")
        if value.startswith(SESSION_COOKIE)
    )
    assert all(
        value in cookie for value in ("HttpOnly", "Secure", "SameSite=lax", "Path=/", "Max-Age=")
    )
    assert "Domain=" not in cookie
    token = client.cookies.get(SESSION_COOKIE)
    assert re.fullmatch(r"[A-Za-z0-9_-]{43}", token)
    assert token not in response.text
    assert response.json() == session_view(client)
    assert response.json()["user"] == {
        "id": str(user_id),
        "display_name": "Học viên",
        "locale": "vi",
        "timezone": "UTC",
        "roles": ["learner"],
        "verified": True,
        "onboarding_completed": False,
    }
    with identity_engine.connect() as connection:
        (digest, owner, revoked_at) = connection.execute(
            text("SELECT token_digest, user_id, revoked_at FROM auth_sessions")
        ).one()
    assert (digest, owner, revoked_at) == (digest_token(token), user_id, None)


def test_user_view_only_projects_the_current_users_onboarding_preferences(
    browser_factory, create_user, identity_engine
):
    owner = create_user(EMAIL)
    other_email = "second@example.com"
    create_user(other_email)
    with Session(identity_engine) as session, session.begin():
        session.add(
            LearningPreferences(
                user_id=owner,
                locale="en",
                timezone="Asia/Ho_Chi_Minh",
                current_cefr="B1",
                onboarding_completed_at=datetime.now(UTC),
            )
        )

    first, second = browser_factory(), browser_factory()
    assert login(first, EMAIL).status_code == login(second, other_email).status_code == 200
    owner_view = session_view(first)["user"]
    other_view = session_view(second)["user"]

    assert (owner_view["locale"], owner_view["timezone"], owner_view["onboarding_completed"]) == (
        "en",
        "Asia/Ho_Chi_Minh",
        True,
    )
    assert (other_view["locale"], other_view["timezone"], other_view["onboarding_completed"]) == (
        "vi",
        "UTC",
        False,
    )


def test_missing_pending_and_wrong_credentials_return_identical_failures(
    browser_factory, create_user
):
    create_user(EMAIL)
    pending = "pending@example.com"
    create_user(pending, active=False)
    client = browser_factory()

    responses = (
        login(client, "unknown@example.com"),
        login(client, pending),
        login(client, EMAIL, "incorrect learner password"),
    )
    failures = [assert_problem(response, 401, "INVALID_CREDENTIALS") for response in responses]
    assert failures[0] == failures[1] == failures[2]
    assert client.cookies.get(SESSION_COOKIE) is None
    assert session_view(client)["user"] is None


def test_login_rotates_fixed_and_existing_session_cookies(browser_factory, create_user):
    create_user(EMAIL)
    client = browser_factory()
    fixed = "f" * 43
    replay_cookie(client, fixed)
    guest = session_view(client)
    assert guest["user"] is None
    first = login(client, EMAIL)
    assert first.status_code == 200
    old_cookie = client.cookies.get(SESSION_COOKIE)
    assert old_cookie != fixed
    assert first.json()["csrf_token"] != guest["csrf_token"]

    rotated = login(client, EMAIL)

    assert rotated.status_code == 200
    assert client.cookies.get(SESSION_COOKIE) not in (fixed, old_cookie)
    assert rotated.json()["csrf_token"] != first.json()["csrf_token"]
    for obsolete in (fixed, old_cookie):
        replay = browser_factory()
        replay_cookie(replay, obsolete)
        assert session_view(replay)["user"] is None
    assert session_view(client)["user"] == rotated.json()["user"]


@pytest.mark.parametrize("state", ["idle-expired", "hard-expired", "revoked"])
def test_missing_expired_or_revoked_cookie_is_a_guest(
    state, browser_factory, create_user, identity_engine
):
    create_user(EMAIL)
    client = browser_factory()
    assert session_view(client)["user"] is None
    assert login(client, EMAIL).status_code == 200
    token = client.cookies.get(SESSION_COOKIE)
    now = datetime.now(UTC)
    values = {
        "idle-expired": "last_seen_at = :stale",
        "hard-expired": "expires_at = :past, last_seen_at = :recent",
        "revoked": "revoked_at = :now",
    }
    with identity_engine.begin() as connection:
        connection.execute(
            text(f"UPDATE auth_sessions SET {values[state]} WHERE token_digest = :digest"),
            {
                "now": now,
                "past": now - timedelta(seconds=1),
                "recent": now - timedelta(days=1),
                "stale": now - timedelta(days=15),
                "digest": digest_token(token),
            },
        )

    assert session_view(client)["user"] is None


@pytest.mark.parametrize("operation", ["login", "password/forgot", "password/reset"])
@pytest.mark.parametrize(
    "invalid", ["missing-cookie", "missing-csrf", "invalid-csrf", "missing-origin", "cross-origin"]
)
def test_guest_mutations_reject_missing_or_cross_origin_credentials(
    operation, invalid, browser_factory, identity_engine
):
    client = browser_factory()
    headers = {"X-CSRF-Token": session_view(client)["csrf_token"]}
    if invalid == "missing-cookie":
        client.cookies.clear()
    elif invalid == "missing-csrf":
        headers.clear()
    elif invalid == "invalid-csrf":
        headers["X-CSRF-Token"] = "mismatch"
    elif invalid == "missing-origin":
        del client.headers["Origin"]
    else:
        headers["Origin"] = "https://learn.example.com.evil.test"
    payloads = {
        "login": {"email": EMAIL, "password": PASSWORD},
        "password/forgot": {"email": EMAIL},
        "password/reset": {"token": "unknown-proof", "password": PASSWORD},
    }

    response = client.post(f"{AUTH}/{operation}", headers=headers, json=payloads[operation])

    assert_problem(response, 403, "CSRF_REJECTED")
    with identity_engine.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM auth_rate_limits")) == 0


def test_logout_requires_csrf_for_current_session_and_is_idempotent(browser_factory, create_user):
    create_user(EMAIL)
    first, other = browser_factory(), browser_factory()
    guest_token = session_view(first)["csrf_token"]
    one, two = login(first, EMAIL), login(other, EMAIL)
    assert one.status_code == two.status_code == 200
    original = first.cookies.get(SESSION_COOKIE)
    csrf = one.json()["csrf_token"]
    assert csrf != two.json()["csrf_token"]
    invalid = (
        {},
        {"X-CSRF-Token": "invalid"},
        {"X-CSRF-Token": two.json()["csrf_token"]},
        {"X-CSRF-Token": guest_token},
        {"X-CSRF-Token": csrf, "Origin": "https://other.example.com"},
    )
    for headers in invalid:
        assert_problem(first.post(f"{AUTH}/logout", headers=headers), 403, "CSRF_REJECTED")
    assert session_view(first)["user"] == one.json()["user"]

    logged_out = first.post(f"{AUTH}/logout", headers={"X-CSRF-Token": csrf})
    repeated = first.post(f"{AUTH}/logout")

    assert logged_out.status_code == repeated.status_code == 204
    assert logged_out.content == repeated.content == b""
    assert "Max-Age=0" in logged_out.headers["set-cookie"]
    assert first.cookies.get(SESSION_COOKIE) is None
    replay_cookie(first, original)
    assert session_view(first)["user"] is None
    assert session_view(other)["user"] == two.json()["user"]
    invalid = first.post(f"{AUTH}/logout", headers={"Origin": f"{ORIGIN}.evil.test"})
    assert_problem(invalid, 403, "CSRF_REJECTED")


def test_login_rate_limits_normalized_credentials_even_when_account_does_not_exist(browser_factory):
    client = browser_factory()
    for _ in range(5):
        assert login(client, EMAIL).status_code == 401

    limited = login(client, EMAIL.upper())

    assert_problem(limited, 429, "RATE_LIMITED")
    assert 0 < int(limited.headers["retry-after"]) <= 900
    assert login(client, "unrelated@example.com").status_code == 401
