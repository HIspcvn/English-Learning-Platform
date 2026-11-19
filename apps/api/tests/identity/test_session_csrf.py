from base64 import urlsafe_b64encode
from hashlib import sha256
from hmac import digest
from uuid import UUID


def test_learner_csrf_is_linked_to_session_identity_and_an_independent_secret():
    from app.identity.csrf import session_csrf_token

    session = UUID(int=1)
    secret = bytes(range(32))
    expected = urlsafe_b64encode(digest(secret, session.bytes, sha256)).rstrip(b"=").decode("ascii")

    assert session_csrf_token(session, secret) == expected
    assert session_csrf_token(UUID(int=2), secret) != expected
    assert session_csrf_token(session, bytes(reversed(secret))) != expected
