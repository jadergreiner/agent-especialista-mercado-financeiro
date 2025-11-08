"""Middleware de masking genérico para respostas JSON.

Origin: AG-005 - Implementar middleware de masking (Option A)

Regras: percorre objetos JSON (dict/list) e mascara valores de chaves sensíveis
como 'name', 'email', 'cpf', 'ssn', 'document' por padrão.
"""
from typing import Any
from fastapi import Request
from starlette.responses import Response, JSONResponse
import json
import logging

logger = logging.getLogger(__name__)


SENSITIVE_KEYWORDS = ("name", "email", "cpf", "ssn", "document", "phone", "telefone")


def _mask_value(key: str, val: Any) -> Any:
    if val is None:
        return None
    try:
        s = str(val)
    except Exception:
        return val
    k = key.lower()
    if "email" in k:
        parts = s.split("@")
        return (parts[0][:1] + "***@" + parts[1]) if len(parts) > 1 else "***@masked"
    if any(x in k for x in ("cpf", "ssn", "document")):
        return "***-***-" + s[-4:]
    if any(x in k for x in ("name",)):
        return s[:1] + "***"
    if any(x in k for x in ("phone", "telefone")):
        return "(*** ) " + s[-4:]
    # fallback: return original
    return val


def _mask_obj(obj: Any) -> Any:
    # Recursively mask dicts and lists
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if any(keyword in k.lower() for keyword in SENSITIVE_KEYWORDS):
                out[k] = _mask_value(k, v)
            else:
                out[k] = _mask_obj(v)
        return out
    elif isinstance(obj, list):
        return [_mask_obj(v) for v in obj]
    else:
        return obj


def setup_masking_middleware(app):
    @app.middleware("http")
    async def masking_middleware(request: Request, call_next):
        # debug: indicar que middleware de masking foi acionado
        try:
            logger.debug("[masking] processing request: %s %s", request.method, request.url.path)
        except Exception:
            pass
        response = await call_next(request)
        try:
            logger.debug("[masking] got response type=%s, media_type=%s", type(response), getattr(response, 'media_type', None))
        except Exception:
            pass

        # Tentativa genérica: renderizar a resposta e tentar parsear JSON; se for JSON, aplicar masking.
        try:
            rendered = response.render()
            if isinstance(rendered, (bytes, bytearray)):
                rendered_text = rendered.decode(getattr(response, "charset", "utf-8") or "utf-8")
            else:
                rendered_text = str(rendered)
            try:
                content = json.loads(rendered_text)
            except Exception:
                # não é JSON, retornar resposta original
                return response

            try:
                logger.debug("[masking] parsed content keys (generic): %s", (list(content.keys()) if isinstance(content, dict) else type(content)))
            except Exception:
                pass

            masked = _mask_obj(content)
            try:
                logger.debug("[masking] masked sample (generic): %s", (masked.get('name') if isinstance(masked, dict) else None))
            except Exception:
                pass
            return JSONResponse(masked, status_code=response.status_code, headers=dict(response.headers))
        except Exception:
            logger.exception("[masking] generic masking failed")
            return response
