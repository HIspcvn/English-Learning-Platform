from base64 import b64decode
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

API_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=API_ROOT.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    database_url: SecretStr
    auth_public_origin: str = "http://127.0.0.1:3000"
    auth_mail_key: SecretStr | None = None
    auth_mail_key_id: str = Field(default="local-v1", min_length=1, max_length=80)
    smtp_host: str = "127.0.0.1"
    smtp_port: int = Field(default=1025, ge=1, le=65535)
    smtp_sender: str = "no-reply@example.test"

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: SecretStr) -> SecretStr:
        message = "DATABASE_URL must use postgresql+psycopg and name a database"
        try:
            url = make_url(value.get_secret_value())
        except (ArgumentError, ValueError):
            raise ValueError(message) from None
        if url.drivername != "postgresql+psycopg" or not url.database:
            raise ValueError(message)
        return value

    @field_validator("auth_public_origin")
    @classmethod
    def validate_public_origin(cls, value: str) -> str:
        message = "AUTH_PUBLIC_ORIGIN must be an HTTPS origin or an HTTP loopback origin"
        try:
            parsed = urlsplit(value)
            host = parsed.hostname
            port = parsed.port
        except ValueError:
            raise ValueError(message) from None
        if (
            not host
            or parsed.username is not None
            or value != f"{parsed.scheme}://{parsed.netloc}"
            or any(character.isspace() for character in value)
            or port == 0
            or (
                parsed.scheme != "https"
                and (parsed.scheme != "http" or host not in {"localhost", "127.0.0.1", "::1"})
            )
        ):
            raise ValueError(message)
        return value

    @field_validator("auth_mail_key", mode="before")
    @classmethod
    def ignore_blank_mail_key(cls, value: str) -> str | None:
        return value or None

    @field_validator("auth_mail_key")
    @classmethod
    def validate_mail_key(cls, value: SecretStr | None) -> SecretStr | None:
        if value is not None:
            try:
                if len(b64decode(value.get_secret_value(), altchars=b"-_", validate=True)) == 32:
                    return value
            except ValueError:
                pass
            raise ValueError("AUTH_MAIL_KEY must encode 32 bytes in base64")
        return None

    @property
    def auth_mail_key_bytes(self) -> bytes | None:
        if self.auth_mail_key is None:
            return None
        return b64decode(self.auth_mail_key.get_secret_value(), altchars=b"-_", validate=True)
