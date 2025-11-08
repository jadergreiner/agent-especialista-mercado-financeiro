"""Utilities mínimos para mascaramento de dados sensíveis (demo).

Origin: feature/AG-rbac-audit-masking
"""
from typing import Any, Dict

SENSITIVE_KEYS = {"nome_presidente", "cpf", "ssn", "email", "senha", "token", "secret"}

def mask_value(v: Any) -> Any:
    if v is None:
        return v
    # strings are masked, others left as-is for demo
    try:
        if isinstance(v, str):
            return "***MASKED***"
    except Exception:
        return "***MASKED***"
    return v

def mask_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Return a shallow masked copy of dict `d` replacing known sensitive keys.
    Intended for demo masking in responses/logs. Not a substitute for robust PII pipeline.
    """
    out: Dict[str, Any] = {}
    for k, v in d.items():
        if k.lower() in SENSITIVE_KEYS:
            out[k] = mask_value(v)
        else:
            # if nested dict, mask recursively (best-effort)
            if isinstance(v, dict):
                out[k] = mask_dict(v)
            else:
                out[k] = v
    return out
