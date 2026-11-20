from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, Response

from app.errors import ProblemException, documented_problem
from app.identity.csrf import mutation_headers, origin_valid, session_csrf_valid
from app.identity.learner import (
    PUT_PREFERENCES_OPERATION,
    read_preferences,
    read_profile,
    replace_preferences,
    update_profile,
)
from app.identity.learner_schemas import (
    PreferencesView,
    PreferencesWrite,
    ProfileChanges,
    ProfileView,
)
from app.identity.request_session import load_request_session
from app.identity.sessions import SessionIdentity

router = APIRouter(prefix="/api/v1/me", tags=["identity"])
read_errors = {
    401: documented_problem("An active learner session is required."),
    403: documented_problem("The account does not have learner access."),
    503: {
        **documented_problem("The database is unavailable."),
        "headers": {"Retry-After": {"schema": {"type": "integer"}, "description": "Seconds."}},
    },
}
write_errors = {
    **read_errors,
    403: documented_problem("Learner access, Origin or CSRF proof is invalid."),
    422: documented_problem("The request is invalid."),
}


def require_learner(request: Request, response: Response) -> SessionIdentity:
    current = load_request_session(request)
    if current is None:
        raise ProblemException(401, "AUTH_REQUIRED", "An active learner session is required.")
    if "learner" not in current.user.roles or not current.user.verified:
        raise ProblemException(403, "FORBIDDEN", "The account does not have learner access.")
    response.headers["Cache-Control"] = "private, no-store"
    return current


Learner = Annotated[SessionIdentity, Depends(require_learner)]


def require_csrf(request: Request, current: Learner) -> SessionIdentity:
    if not origin_valid(request) or not session_csrf_valid(
        request, current.id, current.csrf_secret
    ):
        raise ProblemException(403, "CSRF_REJECTED", "The request was rejected.")
    return current


LearnerMutation = Annotated[SessionIdentity, Depends(require_csrf)]
IdempotencyKey = Annotated[
    str, Header(alias="Idempotency-Key", min_length=16, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")
]


@router.get("/profile", operation_id="getLearnerProfile", responses=read_errors)
def get_learner_profile(request: Request, current: Learner) -> ProfileView:
    return read_profile(request.app.state.engine, current.user.id)


@router.patch(
    "/profile",
    operation_id="patchLearnerProfile",
    responses={
        **write_errors,
        404: documented_problem("The avatar asset or profile was not found."),
    },
    openapi_extra=mutation_headers(),
)
def patch_learner_profile(
    request: Request, current: LearnerMutation, data: ProfileChanges
) -> ProfileView:
    return update_profile(request.app.state.engine, current, data)


@router.get("/preferences", operation_id="getLearningPreferences", responses=read_errors)
def get_learning_preferences(request: Request, current: Learner) -> PreferencesView:
    return read_preferences(request.app.state.engine, current.user.id)


@router.put(
    "/preferences",
    operation_id=PUT_PREFERENCES_OPERATION,
    responses={
        **write_errors,
        409: documented_problem("The revision is stale or the key conflicts."),
    },
    openapi_extra=mutation_headers(),
)
def put_learning_preferences(
    request: Request,
    current: LearnerMutation,
    data: PreferencesWrite,
    idempotency_key: IdempotencyKey,
) -> PreferencesView:
    if len(request.headers.getlist("Idempotency-Key")) != 1:
        raise ProblemException(422, "VALIDATION_ERROR", "Exactly one idempotency key is required.")
    return replace_preferences(request.app.state.engine, current, data, idempotency_key)
