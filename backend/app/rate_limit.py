"""Per-user rate limiting via SlowAPI.

Protects the LLM bill and signals abuse-awareness. The generation endpoint is
capped at ``DAILY_GENERATION_LIMIT`` per user per day. The limiter is keyed on
the authenticated user (JWT subject), falling back to client IP when the token
is missing or its signature won't verify.
"""
from __future__ import annotations

import jwt
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from .auth import _decode
from .config import settings


def _user_key(request: Request) -> str:
    """Key by VERIFIED JWT subject so the cap is per-user, not per-IP.

    Verifying the signature here matters because slowapi runs before our
    auth dependency; without verification, an attacker could shift their
    own bucket by minting tokens with arbitrary ``sub`` claims. They still
    cannot authenticate (that goes through ``get_current_user``), but the
    accounting would be off. If verification fails, fall back to IP.
    """
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        token = auth[7:]
        try:
            payload = _decode(token)
            sub = payload.get("sub")
            if sub:
                return f"user:{sub}"
        except jwt.PyJWTError:
            pass
    return get_remote_address(request)


limiter = Limiter(key_func=_user_key)


def daily_generation_limit() -> str:
    return f"{settings.daily_generation_limit}/day"
