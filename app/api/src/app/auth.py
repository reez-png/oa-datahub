import os
import time
from functools import lru_cache
from typing import Optional

import httpx
from jose import jwt
from fastapi import HTTPException, Header

AUTH_MODE = os.getenv("AUTH_MODE", "prod")  # prod | dev-noverify
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
JWKS_URL = os.getenv("SUPABASE_JWKS_URL")   # only used if you enable JWKs later

# ---- JWKs helpers (unused if you do HS256) ----------------------------------
@lru_cache(maxsize=1)
def _jwks_cached():
    if not JWKS_URL:
        raise RuntimeError("SUPABASE_JWKS_URL not set")
    with httpx.Client(timeout=5) as c:
        return c.get(JWKS_URL).json()

def _get_key(kid: str):
    jwks = _jwks_cached()
    for k in jwks.get("keys", []):
        if k.get("kid") == kid:
            return k
    return None

def _verify_jwks_token(token: str) -> dict:
    headers = jwt.get_unverified_header(token)
    key = _get_key(headers.get("kid"))
    if not key:
        raise HTTPException(status_code=401, detail="Invalid token (kid)")
    claims = jwt.decode(token, key, algorithms=[key["alg"]], options={"verify_aud": False})
    if claims.get("exp") and time.time() > claims["exp"]:
        raise HTTPException(status_code=401, detail="Token expired")
    return claims

# ---- HS256 (Supabase default) -----------------------------------------------
def _verify_hs256_token(token: str) -> dict:
    if not JWT_SECRET:
        raise HTTPException(status_code=500, detail="JWT secret not configured")
    try:
        claims = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options={"verify_aud": False})
        if claims.get("exp") and time.time() > claims["exp"]:
            raise HTTPException(status_code=401, detail="Token expired")
        return claims
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# ---- Public dependency -------------------------------------------------------
async def require_user(
    authorization: Optional[str] = Header(None),
    x_dev_email: Optional[str] = Header(None),
) -> dict:
    # Dev mode: header shortcut for local testing
    if AUTH_MODE == "dev-noverify":
        if not x_dev_email:
            raise HTTPException(status_code=401, detail="Missing x-dev-email (dev mode)")
        return {"sub": "dev-user", "email": x_dev_email}

    # Prod: need a Bearer token
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()

    # Prefer HS256 (Supabase default). If you later switch to JWKs, set JWKS_URL.
    if JWT_SECRET:
        return _verify_hs256_token(token)
    if JWKS_URL:
        return _verify_jwks_token(token)

    raise HTTPException(status_code=500, detail="Auth not configured")
