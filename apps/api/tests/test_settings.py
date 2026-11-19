import pytest
from pydantic import ValidationError

from app.config import Settings


@pytest.mark.parametrize(
    "url",
    [
        "postgresql://test:private-fixture@localhost/test",
        "postgresql+psycopg://test:private-fixture@localhost",
        "invalid-private-fixture",
    ],
)
def test_database_url_validation_does_not_disclose_input(monkeypatch, url):
    monkeypatch.setenv("DATABASE_URL", url)

    with pytest.raises(ValidationError, match="must use postgresql\\+psycopg") as caught:
        Settings()

    assert "private-fixture" not in str(caught.value)
