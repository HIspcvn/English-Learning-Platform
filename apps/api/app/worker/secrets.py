import os
from datetime import UTC, datetime
from uuid import UUID

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _associated_data(user_id: UUID, token_id: UUID, purpose: str, expires_at: datetime) -> bytes:
    expires_utc = expires_at.astimezone(UTC).isoformat(timespec="microseconds")
    return f"elp:auth-mail:v1:{user_id}:{token_id}:{purpose}:{expires_utc}".encode("ascii")


def encrypt_token(
    key: bytes,
    token: str,
    *,
    user_id: UUID,
    token_id: UUID,
    purpose: str,
    expires_at: datetime,
) -> tuple[bytes, bytes]:
    nonce = os.urandom(12)
    context = _associated_data(user_id, token_id, purpose, expires_at)
    return AESGCM(key).encrypt(nonce, token.encode("ascii"), context), nonce


def decrypt_token(
    key: bytes,
    ciphertext: bytes,
    nonce: bytes,
    *,
    user_id: UUID,
    token_id: UUID,
    purpose: str,
    expires_at: datetime,
) -> str:
    context = _associated_data(user_id, token_id, purpose, expires_at)
    return AESGCM(key).decrypt(nonce, ciphertext, context).decode("ascii")
