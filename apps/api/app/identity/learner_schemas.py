from datetime import date, datetime
from functools import cache
from typing import Annotated, Literal, Self, TypedDict
from uuid import UUID
from zoneinfo import available_timezones

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    field_validator,
    model_validator,
)

from app.identity.schemas import DisplayName, validate_plain_text

Locale = Literal["vi", "en"]
Cefr = Literal["A1", "A2", "B1", "B2", "C1", "C2"]
Accent = Literal["uk", "us", "system"]
TargetKind = Literal["general", "exam"]
ExamCode = Literal["ielts", "toeic"]
Bio = Annotated[str, Field(max_length=500), AfterValidator(validate_plain_text)]


class ProfileView(BaseModel):
    display_name: str
    avatar_asset_id: UUID | None
    bio: str | None


class ProfilePatch(TypedDict, total=False):
    __pydantic_config__ = ConfigDict(extra="forbid", hide_input_in_errors=True)

    display_name: DisplayName
    avatar_asset_id: UUID | None
    bio: Bio | None


def require_profile_changes(value: ProfilePatch) -> ProfilePatch:
    if not value:
        raise ValueError("At least one profile field is required")
    return value


ProfileChanges = Annotated[
    ProfilePatch,
    AfterValidator(require_profile_changes),
    Field(json_schema_extra={"minProperties": 1}),
]


@cache
def valid_timezones() -> set[str]:
    return available_timezones()


class PreferencesWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    locale: Locale
    timezone: str = Field(min_length=1, max_length=128)
    current_cefr: Cefr
    target_kind: TargetKind | None = None
    target_code: ExamCode | None = None
    exam_date: date | None = None
    default_accent: Accent
    ai_opt_in: StrictBool
    social_opt_in: StrictBool
    expected_revision: int = Field(ge=0, strict=True)

    @field_validator("timezone")
    @classmethod
    def iana_timezone(cls, value: str) -> str:
        if value not in valid_timezones():
            raise ValueError("An IANA timezone is required")
        return value

    @field_validator("exam_date", mode="before")
    @classmethod
    def calendar_date(cls, value: object) -> object:
        if value is None or type(value) is date:
            return value
        if isinstance(value, str):
            try:
                parsed = date.fromisoformat(value)
            except ValueError:
                pass
            else:
                if parsed.isoformat() == value:
                    return parsed
        raise ValueError("The exam date must use YYYY-MM-DD")

    @model_validator(mode="after")
    def validate_target(self) -> Self:
        if self.target_kind == "exam":
            if self.target_code is None:
                raise ValueError("An exam code is required when preparing for an exam")
        elif self.target_code is not None or self.exam_date is not None:
            raise ValueError("Exam code and date are only available for exam preparation")
        return self


class PreferencesView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    locale: Locale
    timezone: str
    current_cefr: Cefr | None
    target_kind: TargetKind | None
    target_code: ExamCode | None
    exam_date: date | None
    default_accent: Accent
    ai_opt_in: bool
    social_opt_in: bool
    onboarding_completed_at: datetime | None
    revision: int
