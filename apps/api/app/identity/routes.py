from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from app.errors import Problem, problem_response
from app.identity.csrf import (
    guest_csrf_valid,
    issue_guest_csrf,
    origin_valid,
    session_csrf_token,
    session_csrf_valid,
    valid_guest_value,
)
from app.identity.rate_limit import retry_after
from app.identity.recovery import request_password_reset, reset_password
from app.identity.schemas import (
    Accepted,
    AuthenticatedSession,
    EmailRequest,
    GuestSession,
    LoginRequest,
    PasswordResetRequest,
    VerificationRequest,
)
from app.identity.service import request_verification, verify_account
from app.identity.sessions import (
    HARD_TTL,
    SessionIdentity,
    load_session,
    login_account,
    logout_session,
)

router = APIRouter(prefix="/api/v1/auth", tags=["identity"])


def documented_problem(description: str) -> dict:
    return {
        "description": description,
        "content": {"application/problem+json": {"schema": Problem.model_json_schema()}},
    }


retry_header = {"Retry-After": {"schema": {"type": "integer"}, "description": "Seconds."}}
unavailable_error = {
    **documented_problem("An identity dependency is unavailable."),
    "headers": retry_header,
}
mutation_errors = {
    403: documented_problem("The Origin or CSRF proof is invalid."),
    422: documented_problem("The request body is invalid."),
    429: {
        **documented_problem("The request limit has been reached."),
        "headers": retry_header,
    },
    503: unavailable_error,
}
cookie_header = {
    "Set-Cookie": {
        "schema": {"type": "string"},
        "description": "Host-only HttpOnly session cookie. Secure on HTTPS and SameSite=Lax.",
    }
}
private_headers = {"Cache-Control": "private, no-store"}


def mutation_headers(*, csrf_required: bool = True) -> dict:
    return {
        "parameters": [
            {"name": name, "in": "header", "required": required, "schema": {"type": "string"}}
            for name, required in (("Origin", True), ("X-CSRF-Token", csrf_required))
        ]
    }


def _secure_cookie(request: Request) -> bool:
    return request.app.state.settings.auth_public_origin.startswith("https://")


def _session_cookie_name(request: Request) -> str:
    return "__Host-elp_session" if _secure_cookie(request) else "elp_session_local"


def _session(request: Request, *, touch: bool = False) -> SessionIdentity | None:
    token = request.cookies.get(_session_cookie_name(request), "")
    if not valid_guest_value(token):
        return None
    return load_session(request.app.state.engine, token, touch=touch)


def _mutation_session(
    request: Request, *, logout: bool = False
) -> tuple[SessionIdentity | None, bool]:
    if not origin_valid(request):
        return None, False
    current = _session(request)
    if current is None:
        return None, logout or guest_csrf_valid(request)
    return current, session_csrf_valid(request, current.id, current.csrf_secret)


def _mutation_allowed(request: Request) -> bool:
    return _mutation_session(request)[1]


Allowed = Annotated[bool, Depends(_mutation_allowed)]


def _authenticated_session(current: SessionIdentity) -> AuthenticatedSession:
    return AuthenticatedSession(
        user=current.user, csrf_token=session_csrf_token(current.id, current.csrf_secret)
    )


@router.get("/session", operation_id="getAuthSession", responses={503: unavailable_error})
def get_auth_session(request: Request, response: Response) -> GuestSession | AuthenticatedSession:
    response.headers.update(private_headers)
    current = _session(request, touch=True)
    if current is not None:
        return _authenticated_session(current)
    return GuestSession(user=None, csrf_token=issue_guest_csrf(request, response))


def mutation_denial(
    request: Request, allowed: bool, *, email: str | None = None, scope: str | None = None
) -> Response | None:
    if not allowed:
        return problem_response(request, 403, "CSRF_REJECTED", "The guest request was rejected.")
    peer = request.client.host if request.client is not None else "unknown"
    wait = retry_after(request.app.state.engine, peer, email, scope=scope)
    if wait is not None:
        return problem_response(
            request, 429, "RATE_LIMITED", "Try again later.", headers={"Retry-After": str(wait)}
        )
    return None


@router.post(
    "/login",
    operation_id="login",
    response_model=AuthenticatedSession,
    responses={
        **mutation_errors,
        200: {"headers": cookie_header},
        401: documented_problem("The credentials are invalid or the account is unavailable."),
    },
    openapi_extra=mutation_headers(),
)
def login(
    request: Request, response: Response, data: LoginRequest
) -> AuthenticatedSession | Response:
    previous, allowed = _mutation_session(request)
    denial = mutation_denial(request, allowed, email=data.email, scope="login")
    if denial is not None:
        return denial
    result = login_account(
        request.app.state.engine,
        data.email,
        data.password.get_secret_value(),
        previous.id if previous is not None else None,
    )
    if result is None:
        return problem_response(request, 401, "INVALID_CREDENTIALS", "The credentials are invalid.")

    token, current = result
    response.headers.update(private_headers)
    response.set_cookie(
        _session_cookie_name(request),
        token,
        max_age=int(HARD_TTL.total_seconds()),
        path="/",
        secure=_secure_cookie(request),
        httponly=True,
        samesite="lax",
    )
    return _authenticated_session(current)


@router.post(
    "/logout",
    operation_id="logout",
    status_code=204,
    response_class=Response,
    responses={
        204: {"headers": cookie_header},
        403: mutation_errors[403],
        503: unavailable_error,
    },
    openapi_extra=mutation_headers(csrf_required=False),
)
def logout(request: Request) -> Response:
    current, allowed = _mutation_session(request, logout=True)
    if not allowed:
        return problem_response(request, 403, "CSRF_REJECTED", "The request was rejected.")
    if current is not None:
        logout_session(request.app.state.engine, current.id)
    response = Response(status_code=204, headers=private_headers)
    response.delete_cookie(
        _session_cookie_name(request),
        path="/",
        secure=_secure_cookie(request),
        httponly=True,
        samesite="lax",
    )
    return response


def _mail_unavailable(request: Request) -> Response:
    return problem_response(
        request,
        503,
        "SERVICE_NOT_READY",
        "Email delivery is unavailable.",
        headers={"Retry-After": "60"},
    )


@router.post(
    "/password/forgot",
    operation_id="forgotPassword",
    status_code=202,
    response_model=Accepted,
    responses=mutation_errors,
    openapi_extra=mutation_headers(),
)
def forgot_password(
    request: Request, response: Response, data: EmailRequest, allowed: Allowed
) -> Accepted | Response:
    denial = mutation_denial(request, allowed, email=data.email, scope="recovery-mail")
    if denial is not None:
        return denial
    settings = request.app.state.settings
    key = settings.auth_mail_key_bytes
    if key is None:
        return _mail_unavailable(request)
    request_password_reset(request.app.state.engine, data.email, key, settings.auth_mail_key_id)
    response.headers.update(private_headers)
    return Accepted(accepted=True)


@router.post(
    "/password/reset",
    operation_id="resetPassword",
    status_code=204,
    response_class=Response,
    responses={**mutation_errors, 410: documented_problem("The reset proof is unavailable.")},
    openapi_extra=mutation_headers(),
)
def complete_password_reset(
    request: Request, data: PasswordResetRequest, allowed: Allowed
) -> Response:
    denial = mutation_denial(request, allowed, scope="reset")
    if denial is not None:
        return denial
    if not reset_password(
        request.app.state.engine, data.token.get_secret_value(), data.password.get_secret_value()
    ):
        return problem_response(
            request, 410, "TOKEN_UNAVAILABLE", "The password reset link is invalid."
        )
    return Response(status_code=204, headers=private_headers)


def accept_email(
    request: Request, response: Response, data: EmailRequest, allowed: bool, *, register: bool
) -> Accepted | Response:
    denial = mutation_denial(request, allowed, email=data.email)
    if denial is not None:
        return denial
    settings = request.app.state.settings
    key = settings.auth_mail_key_bytes
    if key is None:
        return _mail_unavailable(request)
    request_verification(
        request.app.state.engine, data.email, key, settings.auth_mail_key_id, register=register
    )
    response.headers["Cache-Control"] = "no-store"
    return Accepted(accepted=True)


@router.post(
    "/register",
    operation_id="registerEmail",
    status_code=202,
    response_model=Accepted,
    responses=mutation_errors,
    openapi_extra=mutation_headers(),
)
def register_email(
    request: Request, response: Response, data: EmailRequest, allowed: Allowed
) -> Accepted | Response:
    return accept_email(request, response, data, allowed, register=True)


@router.post(
    "/verification/resend",
    operation_id="resendEmailVerification",
    status_code=202,
    response_model=Accepted,
    responses=mutation_errors,
    openapi_extra=mutation_headers(),
)
def resend_email_verification(
    request: Request, response: Response, data: EmailRequest, allowed: Allowed
) -> Accepted | Response:
    return accept_email(request, response, data, allowed, register=False)


@router.post(
    "/verify",
    operation_id="verifyEmail",
    status_code=204,
    response_class=Response,
    responses={
        **mutation_errors,
        410: documented_problem("The verification proof is unavailable."),
    },
    openapi_extra=mutation_headers(),
)
def verify_email(request: Request, data: VerificationRequest, allowed: Allowed) -> Response:
    denial = mutation_denial(request, allowed)
    if denial is not None:
        return denial
    if not verify_account(
        request.app.state.engine,
        data.token.get_secret_value(),
        data.password.get_secret_value(),
        data.display_name,
    ):
        return problem_response(
            request, 410, "TOKEN_UNAVAILABLE", "The verification link is invalid."
        )
    return Response(status_code=204, headers={"Cache-Control": "no-store"})
