import pytest

from app.identity import routes

from .helpers import AUTH, mutate

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    ("active", "elapsed", "delay"),
    [(True, 0.08, [0.17]), (False, 0.02, [0.23]), (True, 0.35, [])],
)
def test_recovery_accepted_responses_share_a_timing_floor(
    active, elapsed, delay, browser_factory, create_user, monkeypatch
):
    email = "recovery@example.com"
    if active:
        create_user(email)
    client = browser_factory()
    calls = []
    readings = iter((100.0, 100.0 + elapsed))

    async def record_sleep(seconds):
        calls.append(seconds)

    monkeypatch.setattr(routes, "monotonic", lambda: next(readings), raising=False)
    monkeypatch.setattr(routes, "sleep", record_sleep, raising=False)

    response = mutate(client, "password/forgot", {"email": email})

    assert response.status_code == 202
    assert response.json() == {"accepted": True}
    assert calls == pytest.approx(delay)


def test_recovery_rejection_does_not_wait_for_timing_floor(browser_factory, monkeypatch):
    client = browser_factory()
    calls = []

    async def record_sleep(seconds):
        calls.append(seconds)

    monkeypatch.setattr(routes, "sleep", record_sleep, raising=False)

    response = client.post(f"{AUTH}/password/forgot", json={"email": "recovery@example.com"})

    assert response.status_code == 403
    assert calls == []
