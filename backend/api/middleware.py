"""
# Origin: AG-004 - Middleware de auditoria

Middleware que injeta um `X-Request-Id` e registra eventos de auditoria para cada request.
Não grava payloads sensíveis — apenas resumo breve.
"""
from fastapi import Request
from uuid import uuid4
from datetime import datetime
from backend.api.audit import save_event


def setup_audit_middleware(app):
    @app.middleware("http")
    async def audit_middleware(request: Request, call_next):
        request_id = str(uuid4())
        # extrair usuário do header (mock)
        username = request.headers.get("x-user") or "anonymous"
        ip = None
        try:
            client = request.client
            if client:
                ip = client.host
        except Exception:
            ip = None

        # chamar rota
        response = await call_next(request)

        # resumo: método, path e status
        summary = f"{request.method} {request.url.path}"

        # salvar evento de auditoria (não-bloqueante no fluxo simples)
        try:
            save_event(
                timestamp=datetime.utcnow().isoformat(),
                username=username,
                endpoint=request.url.path,
                method=request.method,
                status=response.status_code,
                request_id=request_id,
                ip=ip,
                summary=summary,
            )
        except Exception:
            # não interromper a resposta por falha de auditoria
            pass

        # expor request id na resposta
        response.headers["X-Request-Id"] = request_id
        return response
