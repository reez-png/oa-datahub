# app/api/src/app/auth.py
import os
import time
from functools import lru_cache
from typing import Optional

import httpx
from jose import jwt
from fastapi import HTTPException, Header

JWKS_URL = os.getenv("SUPABASE_JWKS_URL")
AUTH_MODE = os.getenv("AUTH_MODE", "prod")  # "dev-noverify" | "prod"


@lru_cache(maxsize=1)
def _jwks_cached():
    if not JWKS_URL:
        raise RuntimeError("SUPABASE_JWKS_URL not set")
    with httpx.Client(timeout=5) as c:
        return c.get(JWKS_URL).json()


def _get_key(kid: str):
    jwks = _jwks_cached()
    for k in jwks["keys"]:
        if k["kid"] == kid:
            return k
    return None


def verify_jwt(token: str) -> dict:
    try:
        headers = jwt.get_unverified_header(token)
        key = _get_key(headers.get("kid"))
        if not key:
            raise HTTPException(status_code=401, detail="Invalid token (kid)")
        claims = jwt.decode(token, key, algorithms=[key["alg"]], options={"verify_aud": False})
        if claims.get("exp") and time.time() > claims["exp"]:
            raise HTTPException(status_code=401, detail="Token expired")
        return claims
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


async def require_user(
    authorization: Optional[str] = Header(None),
    x_dev_email: Optional[str] = Header(None),
) -> dict:
    """
    - dev-noverify: trust 'x-dev-email' header for local dev (no JWT validation).
    - prod: require a valid Bearer JWT signed by Supabase (JWKS).
    """
    if AUTH_MODE == "dev-noverify":
        if not x_dev_email:
            raise HTTPException(status_code=401, detail="Missing x-dev-email (dev mode)")
        return {"sub": "dev-user", "email": x_dev_email}

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    return verify_jwt(token)
