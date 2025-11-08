"""
# Origin: AG-003 - Autenticacao minima baseada em token HMAC (sem dependencias externas)

Fornece utilitários leves para criar e validar tokens assinados (formato JSON+HMAC).
Este token é somente para ambientes de desenvolvimento/staging; em produção substitua
por OAuth2/OpenID Connect / JWT compatível.
"""
import os
import json
import base64
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

SECRET_KEY = os.environ.get("AG_SECRET_KEY", "dev-secret-key-change-this")


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_token(payload: Dict[str, Any], expires_minutes: int = 60) -> str:
    data = payload.copy()
    data['exp'] = (datetime.utcnow() + timedelta(minutes=expires_minutes)).isoformat()
    json_bytes = json.dumps(data, separators=(',', ':')).encode('utf-8')
    payload_b64 = _b64encode(json_bytes)
    sig = hmac.new(SECRET_KEY.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).digest()
    sig_b64 = _b64encode(sig)
    return f"{payload_b64}.{sig_b64}"


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload_b64, sig_b64 = token.split('.')
        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64decode(sig_b64), expected_sig):
            return None
        json_bytes = _b64decode(payload_b64)
        data = json.loads(json_bytes.decode('utf-8'))
        exp = datetime.fromisoformat(data.get('exp'))
        if datetime.utcnow() > exp:
            return None
        return data
    except Exception:
        return None
