import json
from datetime import timedelta
from hashlib import sha256
from typing import get_args
from uuid import UUID

from sqlalchemy import Engine, delete, select, tuple_
from sqlalchemy.orm import Session

from app.errors import ProblemException
from app.identity.learner_schemas import (
    ExamCode,
    PreferencesView,
    PreferencesWrite,
    ProfilePatch,
    ProfileView,
)
from app.identity.models import IdempotencyRecord, LearningPreferences, UserProfile
from app.identity.service import utc_now
from app.identity.sessions import SessionIdentity, lock_active_learner

PUT_PREFERENCES_OPERATION = "putLearningPreferences"
PREFERENCES_RECEIPT_TTL = timedelta(days=7)


def _profile(session: Session, user_id: UUID) -> UserProfile:
    profile = session.get(UserProfile, user_id)
    if profile is None:
        raise ProblemException(404, "NOT_FOUND", "The learner profile was not found.")
    return profile


def read_profile(engine: Engine, user_id: UUID) -> ProfileView:
    with Session(engine) as session:
        profile = _profile(session, user_id)
        return ProfileView(display_name=profile.display_name, avatar_asset_id=None, bio=profile.bio)


def update_profile(engine: Engine, identity: SessionIdentity, data: ProfilePatch) -> ProfileView:
    if data.get("avatar_asset_id") is not None:
        # Avatar ownership and readiness cannot be established before the media catalog exists.
        raise ProblemException(404, "NOT_FOUND", "The avatar asset was not found.")
    with Session(engine) as session, session.begin():
        if not lock_active_learner(session, identity):
            raise ProblemException(401, "AUTH_REQUIRED", "An active learner session is required.")
        profile = _profile(session, identity.user.id)
        if "display_name" in data:
            profile.display_name = data["display_name"]
        if "bio" in data:
            profile.bio = data["bio"]
        return ProfileView(display_name=profile.display_name, avatar_asset_id=None, bio=profile.bio)


def read_preferences(engine: Engine, user_id: UUID) -> PreferencesView:
    with Session(engine) as session:
        preferences = session.get(LearningPreferences, user_id)
        if preferences is not None:
            # The original preferences table allowed targets outside today's choices.
            exam_code = preferences.target_code
            exam = preferences.target_kind == "exam" and exam_code in get_args(ExamCode)
            target_kind = None
            if exam:
                target_kind = "exam"
            elif preferences.target_kind == "general":
                target_kind = "general"
            return PreferencesView(
                locale=preferences.locale,
                timezone=preferences.timezone,
                current_cefr=preferences.current_cefr,
                target_kind=target_kind,
                target_code=exam_code if exam else None,
                exam_date=preferences.exam_date if exam else None,
                default_accent=preferences.default_accent,
                ai_opt_in=preferences.ai_opt_in,
                social_opt_in=preferences.social_opt_in,
                onboarding_completed_at=preferences.onboarding_completed_at,
                revision=preferences.revision,
            )
    return PreferencesView(
        locale="vi",
        timezone="UTC",
        current_cefr=None,
        target_kind=None,
        target_code=None,
        exam_date=None,
        default_accent="system",
        ai_opt_in=False,
        social_opt_in=False,
        onboarding_completed_at=None,
        revision=0,
    )


def replace_preferences(
    engine: Engine, identity: SessionIdentity, data: PreferencesWrite, key: str
) -> PreferencesView:
    content = json.dumps(
        data.model_dump(mode="json", exclude_unset=True), separators=(",", ":"), sort_keys=True
    )
    body_hash = sha256(f"PUT /api/v1/me/preferences\n{content}".encode()).digest()
    owner = identity.user.id
    with Session(engine) as session, session.begin():
        # The owner lock serializes first writes (no preference row yet) and receipt replay.
        if not lock_active_learner(session, identity):
            raise ProblemException(401, "AUTH_REQUIRED", "An active learner session is required.")
        now = utc_now()
        record_key = (owner, PUT_PREFERENCES_OPERATION, key)
        receipt = session.get(IdempotencyRecord, record_key, with_for_update=True)
        if receipt is not None and receipt.expires_at > now:
            if receipt.body_hash != body_hash:
                raise ProblemException(
                    409,
                    "IDEMPOTENCY_CONFLICT",
                    "The idempotency key was already used for a different request.",
                )
            return PreferencesView.model_validate(receipt.response_body)

        preferences = session.get(LearningPreferences, owner, with_for_update=True)
        revision = preferences.revision if preferences is not None else 0
        if revision != data.expected_revision:
            raise ProblemException(409, "STALE_REVISION", "The learning preferences have changed.")
        if (data.ai_opt_in and not (preferences and preferences.ai_opt_in)) or (
            data.social_opt_in and not (preferences and preferences.social_opt_in)
        ):
            raise ProblemException(422, "VALIDATION_ERROR", "This opt-in is not available yet.")

        if preferences is None:
            preferences = LearningPreferences(user_id=owner)
            session.add(preferences)
        for field, value in data.model_dump(exclude={"expected_revision"}).items():
            setattr(preferences, field, value)
        if preferences.onboarding_completed_at is None:
            preferences.onboarding_completed_at = now
        preferences.revision = revision + 1
        result = PreferencesView.model_validate(preferences)

        if receipt is None:
            receipt = IdempotencyRecord(
                user_id=owner, operation_id=PUT_PREFERENCES_OPERATION, idem_key=key
            )
            session.add(receipt)
        receipt.body_hash = body_hash
        receipt.response_status = 200
        receipt.response_body = result.model_dump(mode="json")
        receipt.expires_at = now + PREFERENCES_RECEIPT_TTL
        return result


def retire_expired_receipts(engine: Engine) -> None:
    primary_key = (
        IdempotencyRecord.user_id,
        IdempotencyRecord.operation_id,
        IdempotencyRecord.idem_key,
    )
    expired = (
        select(*primary_key)
        .where(IdempotencyRecord.expires_at <= utc_now())
        .order_by(IdempotencyRecord.expires_at, *primary_key)
        .limit(100)
        .with_for_update(skip_locked=True)
    )
    with engine.begin() as connection:
        connection.execute(delete(IdempotencyRecord).where(tuple_(*primary_key).in_(expired)))
