import hashlib
import hmac
import os
import time
from typing import Optional

import base64
import json


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    salt = salt or os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return _b64url_encode(salt) + ":" + _b64url_encode(dk)


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_b64, hash_b64 = stored.split(":", 1)
        salt = _b64url_decode(salt_b64)
        expected = _b64url_decode(hash_b64)
        test = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return hmac.compare_digest(test, expected)
    except Exception:
        return False


def _sign(data: bytes, secret: bytes) -> bytes:
    return hmac.new(secret, data, hashlib.sha256).digest()


def create_jwt(payload: dict, secret: str, expires_in_seconds: int = 3600) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    exp = int(time.time()) + expires_in_seconds
    body = {**payload, "exp": exp}
    h = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    b = _b64url_encode(json.dumps(body, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{h}.{b}".encode("utf-8")
    sig = _b64url_encode(_sign(signing_input, secret.encode("utf-8")))
    return f"{h}.{b}.{sig}"


def verify_jwt(token: str, secret: str) -> Optional[dict]:
    try:
        h, b, sig = token.split(".", 3)
        signing_input = f"{h}.{b}".encode("utf-8")
        expected = _b64url_encode(_sign(signing_input, secret.encode("utf-8")))
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(_b64url_decode(b))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        return payload
    except Exception:
        return None

