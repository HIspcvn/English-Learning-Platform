from datetime import date

import pytest
from pydantic import TypeAdapter, ValidationError

from app.identity.learner_schemas import PreferencesWrite, ProfileChanges

PROFILE = TypeAdapter(ProfileChanges)
PREFERENCES = {
    "locale": "vi",
    "timezone": "America/New_York",
    "current_cefr": "C2",
    "default_accent": "us",
    "ai_opt_in": False,
    "social_opt_in": False,
    "expected_revision": 0,
}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"display_name": "\x00"},
        {"display_name": "a" * 81},
        {"bio": "\ud800"},
        {"bio": "a" * 501},
    ],
)
def test_profile_changes_reject_empty_or_invalid_text(payload):
    with pytest.raises(ValidationError):
        PROFILE.validate_python(payload)


def test_profile_changes_trim_name_and_preserve_literal_text_and_null():
    assert PROFILE.validate_python({"display_name": "  Học viên   "}) == {
        "display_name": "Học viên",
    }
    assert PROFILE.validate_python({"bio": "<b>Literal text</b>"}) == {"bio": "<b>Literal text</b>"}
    assert PROFILE.validate_python({"bio": None}) == {"bio": None}


@pytest.mark.parametrize(
    "change",
    [
        {"current_cefr": "C3"},
        {"timezone": "UTC+7"},
        {"expected_revision": -1},
        {"expected_revision": True},
        {"ai_opt_in": "false"},
        {"target_kind": "exam", "target_code": "other"},
        {"target_kind": "general", "target_code": "ielts"},
        {"target_kind": "exam", "target_code": "ielts", "exam_date": "2030-02-30"},
        {"target_kind": "exam", "target_code": "toeic", "exam_date": "2030-02-28T00:00:00Z"},
    ],
)
def test_preference_command_rejects_invalid_types_values_and_exam_combinations(change):
    with pytest.raises(ValidationError):
        PreferencesWrite.model_validate({**PREFERENCES, **change})


def test_preference_command_supports_an_iana_zone_and_optional_exam_date():
    preferences = PreferencesWrite.model_validate(PREFERENCES)
    assert preferences.timezone == "America/New_York"
    assert preferences.target_kind is preferences.target_code is preferences.exam_date is None

    exam = PreferencesWrite.model_validate(
        {**PREFERENCES, "target_kind": "exam", "target_code": "toeic"}
    )
    assert exam.target_code == "toeic"
    assert exam.exam_date is None
    scheduled = PreferencesWrite.model_validate(
        {**PREFERENCES, "target_kind": "exam", "target_code": "toeic", "exam_date": "2030-02-28"}
    )
    assert scheduled.exam_date == date(2030, 2, 28)
