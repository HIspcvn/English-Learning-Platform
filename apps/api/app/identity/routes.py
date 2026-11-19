from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from app.errors import Problem, problem_response
from app.identity.csrf import guest_csrf_valid, issue_guest_csrf
from app.identity.rate_limit import retry_after
from app.identity.schemas import Accepted, EmailRequest, GuestSession, VerificationRequest
from app.identity.service import request_verification, verify_account

router = APIRouter(prefix="/api/v1/auth", tags=["identity"])


def documented_problem(description: str) -> dict:
    return {
        "description": description,
        "content": {"application/problem+json": {"schema": Problem.model_json_schema()}},
    }


retry_header = {"Retry-After": {"schema": {"type": "integer"}, "description": "Seconds."}}
mutation_errors = {
    403: documented_problem("The Origin or guest CSRF proof is invalid."),
    422: documented_problem("The request body is invalid."),
    429: {
        **documented_problem("The request limit has been reached."),
        "headers": retry_header,
    },
    503: {
        **documented_problem("An identity dependency is unavailable."),
        "headers": retry_header,
    },
}
guest_headers = {
    "parameters": [
        {"name": name, "in": "header", "required": True, "schema": {"type": "string"}}
        for name in ("Origin", "X-CSRF-Token")
    ]
}
GuestAllowed = Annotated[bool, Depends(guest_csrf_valid)]


@router.get("/session", operation_id="getAuthSession", response_model=GuestSession)
def guest_session(request: Request, response: Response) -> GuestSession:
    response.headers["Cache-Control"] = "private, no-store"
    return GuestSession(user=None, csrf_token=issue_guest_csrf(request, response))


def mutation_denial(
    request: Request, allowed: bool, *, email: str | None = None
) -> Response | None:
    if not allowed:
        return problem_response(request, 403, "CSRF_REJECTED", "The guest request was rejected.")
    peer = request.client.host if request.client is not None else "unknown"
    wait = retry_after(request.app.state.engine, peer, email)
    if wait is not None:
        return problem_response(
            request, 429, "RATE_LIMITED", "Try again later.", headers={"Retry-After": str(wait)}
        )
    return None


def accept_email(
    request: Request, response: Response, data: EmailRequest, allowed: bool, *, register: bool
) -> Accepted | Response:
    denial = mutation_denial(request, allowed, email=data.email)
    if denial is not None:
        return denial
    settings = request.app.state.settings
    key = settings.auth_mail_key_bytes
    if key is None:
        return problem_response(
            request,
            503,
            "SERVICE_NOT_READY",
            "Email delivery is unavailable.",
            headers={"Retry-After": "60"},
        )
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
    openapi_extra=guest_headers,
)
def register_email(
    request: Request, response: Response, data: EmailRequest, allowed: GuestAllowed
) -> Accepted | Response:
    return accept_email(request, response, data, allowed, register=True)


@router.post(
    "/verification/resend",
    operation_id="resendEmailVerification",
    status_code=202,
    response_model=Accepted,
    responses=mutation_errors,
    openapi_extra=guest_headers,
)
def resend_email_verification(
    request: Request, response: Response, data: EmailRequest, allowed: GuestAllowed
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
    openapi_extra=guest_headers,
)
def verify_email(request: Request, data: VerificationRequest, allowed: GuestAllowed) -> Response:
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
