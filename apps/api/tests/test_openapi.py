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
