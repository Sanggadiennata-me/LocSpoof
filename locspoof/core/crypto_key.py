"""
LocSpoof Serverless Cryptographic License Key Engine (Python counterpart).
Mirrors the pure JS implementation with HMAC-SHA256 signatures.
"""

import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict, List, Optional, Tuple

MASTER_SIGNING_SECRET = "LOCSPOOF_SEC_KEY_9d8f3b2a1c7e4a6f9012345678abcdef0123456789abcdef"


def _to_base64url(s: str) -> str:
    return base64.urlsafe_b64encode(s.encode("utf-8")).decode("utf-8").rstrip("=")


def _from_base64url(b64: str) -> str:
    rem = len(b64) % 4
    if rem:
        b64 += "=" * (4 - rem)
    return base64.urlsafe_b64decode(b64.encode("utf-8")).decode("utf-8")


def generate_license_key(
    username: str,
    role: str = "USER",
    duration_days: Optional[int] = None,
    features: Optional[List[str]] = None,
) -> str:
    """Generate a serverless cryptographic license key."""
    if features is None:
        features = ["map", "spoof", "browser", "wireless"]

    now = int(time.time())
    exp = now + duration_days * 86400 if duration_days else 0

    payload = {
        "sub": username.strip().lower(),
        "role": role.upper(),
        "iat": now,
        "exp": exp,
        "feat": features,
    }

    payload_json = json.dumps(payload, separators=(",", ":"))
    payload_b64 = _to_base64url(payload_json)

    sig = hmac.new(
        MASTER_SIGNING_SECRET.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:32]

    return f"LOCSPOOF-{payload['role']}-{payload_b64}-{sig}"


def verify_license_key(raw_key: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Verify cryptographic license key without database."""
    if not raw_key or not isinstance(raw_key, str):
        return False, None, "Key cannot be empty."

    parts = raw_key.strip().split("-")
    if len(parts) < 4 or parts[0] != "LOCSPOOF":
        return False, None, "Invalid key format. Must start with LOCSPOOF-"

    role, payload_b64, signature = parts[1], parts[2], parts[3]

    expected_sig = hmac.new(
        MASTER_SIGNING_SECRET.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:32]

    if not hmac.compare_digest(signature.lower(), expected_sig.lower()):
        return False, None, "Signature mismatch! This key is counterfeit or modified."

    try:
        payload_json = _from_base64url(payload_b64)
        payload = json.loads(payload_json)

        exp = payload.get("exp", 0)
        if exp > 0 and int(time.time()) > exp:
            return False, payload, "This key has expired."

        return True, payload, None
    except Exception as exc:
        return False, None, f"Failed to decode key payload: {exc}"
