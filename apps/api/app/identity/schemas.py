from typing import Annotated, Literal
from uuid import UUID

from email_validator import EmailNotValidError, validate_email
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, SecretStr, field_validator


def validate_utf8(value: str | SecretStr) -> str | SecretStr:
    text = value.get_secret_value() if isinstance(value, SecretStr) else value
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        raise ValueError("Invalid UTF-8 text") from None
    return value


Password = Annotated[SecretStr, Field(min_length=12, max_length=128), AfterValidator(validate_utf8)]


class EmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    email: str = Field(max_length=254, json_schema_extra={"format": "email"})

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        try:
            address = validate_email(value.strip(), check_deliverability=False)
        except (EmailNotValidError, UnicodeError):
            raise ValueError("Invalid email address") from None
        email = f"{address.local_part}@{address.ascii_domain}"
        if len(email.lower().encode("utf-8")) > 254:
            raise ValueError("Invalid email address")
        return email


class VerificationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    token: SecretStr = Field(min_length=1, max_length=128)
    password: Password
    display_name: str = Field(min_length=1, max_length=80)

    @field_validator("display_name", mode="before")
    @classmethod
    def trim_display_name(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if "\x00" in value:
                raise ValueError("Invalid display name")
        return value

    @field_validator("token", "display_name")
    @classmethod
    def validate_utf8(cls, value: str | SecretStr) -> str | SecretStr:
        return validate_utf8(value)


class LoginRequest(EmailRequest):
    password: Password


class Accepted(BaseModel):
    accepted: Literal[True]


class GuestSession(BaseModel):
    user: None
    csrf_token: str


class UserView(BaseModel):
    id: UUID
    display_name: str
    locale: str
    timezone: str
    roles: list[str]
    verified: bool
    onboarding_completed: bool


class AuthenticatedSession(BaseModel):
    user: UserView
    csrf_token: str
