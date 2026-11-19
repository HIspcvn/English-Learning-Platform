AUTH = "/api/v1/auth"
ORIGIN = "https://learn.example.com"
PASSWORD = "synthetic learner password"
MAIL_KEY = bytes(range(32))
SESSION_COOKIE = "__Host-elp_session"


def session_view(client):
    response = client.get(f"{AUTH}/session")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "private, no-store"
    return response.json()


def mutate(client, operation, payload):
    return client.post(
        f"{AUTH}/{operation}",
        headers={"X-CSRF-Token": session_view(client)["csrf_token"]},
        json=payload,
    )


def login(client, email, password=PASSWORD):
    return mutate(client, "login", {"email": email, "password": password})


def replay_cookie(client, token):
    client.cookies.set(SESSION_COOKIE, token, domain="learn.example.com", path="/")


def assert_problem(response, status, code):
    assert response.status_code == status
    assert response.headers["content-type"] == "application/problem+json"
    assert "no-store" in response.headers["cache-control"]
    problem = response.json()
    assert (problem["status"], problem["code"]) == (status, code)
    assert problem["request_id"] == response.headers["x-request-id"]
    return {key: value for key, value in problem.items() if key != "request_id"}
