import json
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

UNREACHABLE_DATABASE = "postgresql+psycopg://test:secret-sentinel@127.0.0.1:1/test"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", UNREACHABLE_DATABASE)
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


def test_liveness_works_without_a_database(client):
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["cache-control"] == "no-store"
    assert UUID(response.headers["x-request-id"])


def test_readiness_returns_safe_problem_when_database_is_unreachable(client):
    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.headers["content-type"] == "application/problem+json"
    assert response.headers["cache-control"] == "no-store"
    assert response.json() == {
        "type": "about:blank",
        "title": "Service Unavailable",
        "status": 503,
        "detail": "The service is not ready.",
        "instance": "/health/ready",
        "code": "SERVICE_NOT_READY",
        "request_id": response.headers["x-request-id"],
    }


def test_unknown_api_route_returns_problem_with_correlated_request_id(client):
    request_id = str(uuid4())
    response = client.get(
        "/api/v1/missing?private=secret-sentinel", headers={"X-Request-ID": request_id}
    )

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    assert response.headers["x-request-id"] == request_id
    assert response.json()["request_id"] == request_id
    assert response.json()["instance"] == "/api/v1/missing"
    assert "secret-sentinel" not in response.text


def test_logs_safe_structured_fields(client, caplog):
    with caplog.at_level("INFO", logger="app.access"):
        response = client.get(
            "/health/live?private=secret-sentinel", headers={"X-Request-ID": "client-sentinel"}
        )

    events = [
        json.loads(record.message) for record in caplog.records if record.name == "app.access"
    ]
    assert len(events) == 1
    assert events[0]["method"] == "GET"
    assert events[0]["status"] == 200
    assert events[0]["request_id"] == response.headers["x-request-id"]
    assert events[0]["duration_ms"] >= 0
    assert "secret-sentinel" not in caplog.text
    assert "client-sentinel" not in caplog.text


def test_openapi_documents_health_and_problem_response(client):
    response = client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "200" in paths["/health/live"]["get"]["responses"]
    assert "200" in paths["/health/ready"]["get"]["responses"]
    assert (
        "application/problem+json" in paths["/health/ready"]["get"]["responses"]["503"]["content"]
    )
