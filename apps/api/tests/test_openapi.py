import json
import subprocess
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]


def test_openapi_export_is_deterministic_without_database_configuration(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"

    for destination in (first, second):
        result = subprocess.run(
            [sys.executable, "-m", "app.export_openapi", "--output", str(destination)],
            cwd=API_ROOT,
            capture_output=True,
            check=False,
            text=True,
            timeout=20,
        )
        assert result.returncode == 0, result.stderr

    schema = first.read_bytes()
    assert schema == second.read_bytes() == (API_ROOT / "openapi.json").read_bytes()
    assert schema.endswith(b"\n") and b"\r" not in schema
    assert "/health/live" in json.loads(schema)["paths"]


def test_auth_schema_exposes_actual_mutation_headers_and_problem_responses():
    from app.main import app

    schema = app.openapi()
    models = schema["components"]["schemas"]
    assert models["Accepted"]["required"] == ["accepted"]
    assert set(models["GuestSession"]["required"]) == {"user", "csrf_token"}
    paths = schema["paths"]
    for path, success in (("register", "202"), ("verification/resend", "202"), ("verify", "204")):
        operation = paths[f"/api/v1/auth/{path}"]["post"]
        assert {
            (parameter["name"], parameter["in"], parameter["required"], parameter["schema"]["type"])
            for parameter in operation["parameters"]
        } == {("Origin", "header", True, "string"), ("X-CSRF-Token", "header", True, "string")}
        assert success in operation["responses"]
        for code in ("403", "422", "429", "503"):
            assert "application/problem+json" in operation["responses"][code]["content"]
    verify = paths["/api/v1/auth/verify"]["post"]["responses"]
    assert "content" not in verify["204"]
    assert "application/problem+json" in verify["410"]["content"]
