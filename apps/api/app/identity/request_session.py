from fastapi import Request

from app.identity.csrf import valid_guest_value
from app.identity.sessions import SessionIdentity, load_session


def secure_cookie(request: Request) -> bool:
    return request.app.state.settings.auth_public_origin.startswith("https://")


def session_cookie_name(request: Request) -> str:
    return "__Host-elp_session" if secure_cookie(request) else "elp_session_local"


def load_request_session(request: Request, *, touch: bool = False) -> SessionIdentity | None:
    token = request.cookies.get(session_cookie_name(request), "")
    if not valid_guest_value(token):
        return None
    return load_session(request.app.state.engine, token, touch=touch)
