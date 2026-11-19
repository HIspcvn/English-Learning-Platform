from base64 import urlsafe_b64encode
from hmac import compare_digest, digest
from re import fullmatch
from secrets import token_urlsafe
from uuid import UUID

from fastapi import Request, Response


def valid_guest_value(value: str) -> bool:
    return fullmatch(r"[A-Za-z0-9_-]{43}", value) is not None


def guest_cookie_name(origin: str) -> str:
    return "__Host-elp_guest_csrf" if origin.startswith("https://") else "elp_guest_csrf_local"


def issue_guest_csrf(request: Request, response: Response) -> str:
    origin = request.app.state.settings.auth_public_origin
    name = guest_cookie_name(origin)
    token = request.cookies.get(name, "")
    if not valid_guest_value(token):
        token = token_urlsafe(32)
    response.set_cookie(
        name, token, path="/", secure=origin.startswith("https://"), httponly=True, samesite="lax"
    )
    return token


def origin_valid(request: Request) -> bool:
    return request.headers.getlist("origin") == [request.app.state.settings.auth_public_origin]


def guest_csrf_valid(request: Request) -> bool:
    expected_origin = request.app.state.settings.auth_public_origin
    csrf_headers = request.headers.getlist("x-csrf-token")
    if not origin_valid(request) or len(csrf_headers) != 1:
        return False
    csrf = csrf_headers[0]
    cookie = request.cookies.get(guest_cookie_name(expected_origin), "")
    return valid_guest_value(csrf) and valid_guest_value(cookie) and compare_digest(csrf, cookie)


def session_csrf_token(session_id: UUID, csrf_secret: bytes) -> str:
    return urlsafe_b64encode(digest(csrf_secret, session_id.bytes, "sha256")).decode().rstrip("=")


def session_csrf_valid(request: Request, session_id: UUID, csrf_secret: bytes) -> bool:
    values = request.headers.getlist("x-csrf-token")
    return (
        len(values) == 1
        and valid_guest_value(values[0])
        and compare_digest(values[0], session_csrf_token(session_id, csrf_secret))
    )
