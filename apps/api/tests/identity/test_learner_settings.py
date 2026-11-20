from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import text

from .helpers import ORIGIN, assert_problem, login, session_view

PROFILE = "/api/v1/me/profile"
PREFERENCES = "/api/v1/me/preferences"
EMAIL = "learner@example.com"
pytestmark = pytest.mark.integration


def preference_command(**changes):
    return {
        "locale": "vi",
        "timezone": "Asia/Ho_Chi_Minh",
        "current_cefr": "B1",
        "default_accent": "system",
        "ai_opt_in": False,
        "social_opt_in": False,
        "expected_revision": 0,
        **changes,
    }


def put_preferences(client, command, *, csrf=None, key=None):
    return client.put(
        PREFERENCES,
        json=command,
        headers={
            "X-CSRF-Token": csrf if csrf is not None else session_view(client)["csrf_token"],
            "Idempotency-Key": key if key is not None else uuid4().hex,
        },
    )


@pytest.fixture
def learner(browser_factory, create_user):
    create_user(EMAIL, "Học viên")
    client = browser_factory()
    assert login(client, EMAIL).status_code == 200
    return client


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ("GET", PROFILE, None),
        ("PATCH", PROFILE, {"display_name": "Guest update"}),
        ("GET", PREFERENCES, None),
        ("PUT", PREFERENCES, preference_command()),
    ],
)
def test_all_learner_routes_require_a_session(browser_factory, method, path, body):
    guest = browser_factory()
    headers = {"X-CSRF-Token": session_view(guest)["csrf_token"], "Idempotency-Key": uuid4().hex}
    response = guest.request(method, path, json=body, headers=headers)

    assert_problem(response, 401, "AUTH_REQUIRED")


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ("PATCH", PROFILE, {"display_name": "Rejected update"}),
        ("PUT", PREFERENCES, preference_command()),
    ],
)
def test_both_mutations_require_origin_and_session_bound_csrf(
    learner, browser_factory, method, path, body
):
    csrf = session_view(learner)["csrf_token"]
    other_session = browser_factory()
    assert login(other_session, EMAIL).status_code == 200
    other_csrf = session_view(other_session)["csrf_token"]
    del learner.headers["Origin"]
    for headers in (
        {"X-CSRF-Token": csrf},
        {"Origin": "https://different.example.com", "X-CSRF-Token": csrf},
        {"Origin": ORIGIN},
        {"Origin": ORIGIN, "X-CSRF-Token": other_csrf},
    ):
        rejected = learner.request(
            method, path, json=body, headers={**headers, "Idempotency-Key": uuid4().hex}
        )
        assert_problem(rejected, 403, "CSRF_REJECTED")

    assert learner.get(PROFILE).json()["display_name"] == "Học viên"
    assert learner.get(PREFERENCES).json()["revision"] == 0


def test_profile_updates_the_current_account_and_supports_clearing_bio(
    learner, browser_factory, create_user
):
    other_email = "other@example.com"
    other_id = create_user(other_email, "Learner two")
    other = browser_factory()
    assert login(other, other_email).status_code == 200
    headers = {"X-CSRF-Token": session_view(learner)["csrf_token"]}
    original = learner.get(PROFILE)
    assert original.status_code == 200
    assert original.headers["cache-control"] == "private, no-store"
    assert original.json() == {"display_name": "Học viên", "bio": None, "avatar_asset_id": None}

    rejected = learner.patch(
        PROFILE, json={"user_id": str(other_id), "display_name": "Overwrite"}, headers=headers
    )
    assert_problem(rejected, 422, "VALIDATION_ERROR")
    updated = learner.patch(
        PROFILE,
        json={"display_name": "  Nguyễn Anh  ", "bio": "Học tiếng Anh mỗi ngày."},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.headers["cache-control"] == "private, no-store"
    assert learner.get(PROFILE).json() == {
        "display_name": "Nguyễn Anh",
        "bio": "Học tiếng Anh mỗi ngày.",
        "avatar_asset_id": None,
    }
    assert session_view(learner)["user"]["display_name"] == "Nguyễn Anh"
    cleared = learner.patch(PROFILE, json={"bio": None}, headers=headers)
    assert cleared.status_code == 200
    assert cleared.json()["bio"] is None
    assert cleared.json()["display_name"] == "Nguyễn Anh"
    assert other.get(PROFILE).json() == {
        "display_name": "Learner two",
        "bio": None,
        "avatar_asset_id": None,
    }


def test_bad_profile_input_returns_a_problem_and_leaves_the_profile_untouched(learner):
    headers = {"X-CSRF-Token": session_view(learner)["csrf_token"]}
    for payload in ({}, {"display_name": "  "}, {"display_name": None}, {"bio": "x" * 501}):
        assert_problem(
            learner.patch(PROFILE, headers=headers, json=payload), 422, "VALIDATION_ERROR"
        )
    assert_problem(
        learner.patch(PROFILE, headers=headers, json={"avatar_asset_id": str(uuid4())}),
        404,
        "NOT_FOUND",
    )
    assert learner.get(PROFILE).json()["display_name"] == "Học viên"


def test_preferences_default_then_complete_without_exam_and_isolate_other_account(
    learner, browser_factory, create_user
):
    other_email = "other@example.com"
    create_user(other_email)
    other = browser_factory()
    assert login(other, other_email).status_code == 200
    initial = learner.get(PREFERENCES)
    assert initial.status_code == 200
    assert initial.headers["cache-control"] == "private, no-store"
    assert initial.json() == {
        "locale": "vi",
        "timezone": "UTC",
        "current_cefr": None,
        "target_kind": None,
        "target_code": None,
        "exam_date": None,
        "default_accent": "system",
        "ai_opt_in": False,
        "social_opt_in": False,
        "onboarding_completed_at": None,
        "revision": 0,
    }
    response = put_preferences(learner, preference_command())
    assert response.status_code == 200
    assert response.headers["cache-control"] == "private, no-store"
    completed = response.json()
    assert completed["current_cefr"] == "B1"
    assert completed["revision"] == 1
    assert completed["target_code"] is None
    assert completed["exam_date"] is None
    assert completed["onboarding_completed_at"]
    assert learner.get(PREFERENCES).json() == completed
    assert session_view(learner)["user"]["onboarding_completed"] is True
    assert session_view(learner)["user"]["timezone"] == "Asia/Ho_Chi_Minh"
    assert other.get(PREFERENCES).json() == initial.json()
    assert session_view(other)["user"]["onboarding_completed"] is False

    updated = put_preferences(
        learner,
        preference_command(
            expected_revision=1,
            locale="en",
            default_accent="uk",
            target_kind="exam",
            target_code="ielts",
            exam_date="2030-05-20",
        ),
    )
    assert updated.status_code == 200
    assert updated.json() == {
        **completed,
        "locale": "en",
        "default_accent": "uk",
        "target_kind": "exam",
        "target_code": "ielts",
        "exam_date": "2030-05-20",
        "revision": 2,
    }
    assert session_view(learner)["user"]["locale"] == "en"


def test_invalid_preferences_are_rejected_before_completing_onboarding(learner):
    for changes in (
        {"timezone": "Mars/Olympus"},
        {"current_cefr": "C3"},
        {"locale": "fr"},
        {"default_accent": "au"},
        {"target_kind": "exam"},
        {"target_code": "ielts"},
        {"ai_opt_in": True},
        {"social_opt_in": True},
    ):
        response = put_preferences(learner, preference_command(**changes))
        assert_problem(response, 422, "VALIDATION_ERROR")

    assert learner.get(PREFERENCES).json()["revision"] == 0
    assert session_view(learner)["user"]["onboarding_completed"] is False


def test_legacy_exam_target_outside_supported_choices_is_readable_without_mutation(
    learner, identity_engine
):
    user_id = session_view(learner)["user"]["id"]
    exam_date = date(2030, 5, 20)
    completed_at = datetime(2026, 11, 19, tzinfo=UTC)
    with identity_engine.begin() as connection:
        connection.execute(
            text("""
                INSERT INTO learning_preferences (
                    user_id, timezone, current_cefr, target_kind, target_code, exam_date,
                    onboarding_completed_at
                ) VALUES (:user_id, 'UTC', 'B1', 'exam', 'toefl', :exam_date, :completed_at)
            """),
            {"user_id": user_id, "exam_date": exam_date, "completed_at": completed_at},
        )

    response = learner.get(PREFERENCES)

    assert response.status_code == 200
    preferences = response.json()
    assert (
        preferences["target_kind"] is preferences["target_code"] is preferences["exam_date"] is None
    )
    assert preferences["current_cefr"] == "B1"
    assert preferences["revision"] == 1
    assert session_view(learner)["user"]["onboarding_completed"] is True
    with identity_engine.connect() as connection:
        assert connection.execute(
            text("SELECT target_kind, target_code, exam_date FROM learning_preferences")
        ).one() == ("exam", "toefl", exam_date)


def test_preferences_replay_returns_original_receipt_and_rejects_stale_revision(learner):
    command = preference_command()
    key = uuid4().hex
    initial = put_preferences(learner, command, key=key)
    assert initial.status_code == 200

    changed = preference_command(expected_revision=1, current_cefr="A2")
    latest = put_preferences(learner, changed)
    assert latest.status_code == 200
    repeated = put_preferences(learner, command, key=key)
    assert repeated.status_code == 200
    assert repeated.json() == initial.json()
    assert_problem(put_preferences(learner, changed, key=key), 409, "IDEMPOTENCY_CONFLICT")
    assert_problem(put_preferences(learner, changed), 409, "STALE_REVISION")
    assert learner.get(PREFERENCES).json() == latest.json()


def test_preference_idempotency_keys_are_required_and_scoped_to_the_learner(
    learner, browser_factory, create_user
):
    csrf = session_view(learner)["csrf_token"]
    command = preference_command()
    missing = learner.put(PREFERENCES, json=command, headers={"X-CSRF-Token": csrf})
    assert_problem(missing, 422, "VALIDATION_ERROR")
    assert_problem(
        put_preferences(learner, command, csrf=csrf, key="too-short"), 422, "VALIDATION_ERROR"
    )
    assert learner.get(PREFERENCES).json()["revision"] == 0

    other_email = "other@example.com"
    create_user(other_email)
    other = browser_factory()
    assert login(other, other_email).status_code == 200
    key = uuid4().hex
    first = put_preferences(learner, command, key=key)
    second = put_preferences(other, preference_command(current_cefr="A1"), key=key)

    assert first.status_code == second.status_code == 200
    assert learner.get(PREFERENCES).json()["current_cefr"] == "B1"
    assert other.get(PREFERENCES).json()["current_cefr"] == "A1"


@pytest.mark.parametrize("revision", [0, 1])
def test_concurrent_preferences_writes_from_two_sessions_have_one_winner(
    learner, browser_factory, revision
):
    second = browser_factory()
    assert login(second, EMAIL).status_code == 200
    if revision:
        assert put_preferences(learner, preference_command()).status_code == 200
    barrier = Barrier(2, timeout=10)

    def compete(client, level):
        csrf = session_view(client)["csrf_token"]
        barrier.wait()
        return put_preferences(
            client, preference_command(expected_revision=revision, current_cefr=level), csrf=csrf
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(compete, learner, "A2")
        other = pool.submit(compete, second, "B2")
        responses = [first.result(timeout=20), other.result(timeout=20)]

    assert sorted(response.status_code for response in responses) == [200, 409]
    winner = next(response for response in responses if response.status_code == 200)
    assert winner.json()["revision"] == revision + 1
    assert learner.get(PREFERENCES).json() == second.get(PREFERENCES).json() == winner.json()
    assert_problem(
        next(response for response in responses if response.status_code == 409),
        409,
        "STALE_REVISION",
    )
