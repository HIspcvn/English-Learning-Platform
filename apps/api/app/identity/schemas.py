from typing import Annotated, Literal
from uuid import UUID

from email_validator import EmailNotValidError, validate_email
from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    SecretStr,
    field_validator,
)


def validate_utf8(value: str | SecretStr) -> str | SecretStr:
    text = value.get_secret_value() if isinstance(value, SecretStr) else value
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        raise ValueError("Invalid UTF-8 text") from None
    return value


Password = Annotated[SecretStr, Field(min_length=12, max_length=128), AfterValidator(validate_utf8)]
ProofToken = Annotated[
    SecretStr, Field(min_length=1, max_length=128), AfterValidator(validate_utf8)
]


def validate_plain_text(value: str) -> str:
    if "\x00" in value:
        raise ValueError("Invalid text")
    validate_utf8(value)
    return value


def trim_display_name(value: object) -> object:
    return value.strip() if isinstance(value, str) else value


DisplayName = Annotated[
    str,
    Field(min_length=1, max_length=80),
    BeforeValidator(trim_display_name),
    AfterValidator(validate_plain_text),
]


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


class PasswordResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    token: ProofToken
    password: Password


class VerificationRequest(PasswordResetRequest):
    display_name: DisplayName


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
