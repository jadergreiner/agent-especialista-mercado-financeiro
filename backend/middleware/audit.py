"""Middleware ASGI mínimo para auditoria demo.

Registra eventos de requisição/resposta em um arquivo local `.logs/audit.log`.
Origin: feature/AG-rbac-audit-masking
"""
import json
import os
import time
from typing import Callable

from starlette.types import ASGIApp, Receive, Scope, Send


class AuditMiddleware:
    def __init__(self, app: ASGIApp, logfile: str = ".logs/audit.log"):
        self.app = app
        self.logfile = logfile
        os.makedirs(os.path.dirname(self.logfile), exist_ok=True)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.time()
        # Collect minimal info
        event = {
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "method": scope.get("method"),
            "path": scope.get("path"),
            "client": scope.get("client"),
        }

        # Use a send wrapper to capture status code
        status_code_holder = {"status": None}

        async def send_wrapper(message):
            if message.get("type") == "http.response.start":
                status_code_holder["status"] = message.get("status")
            await send(message)

        await self.app(scope, receive, send_wrapper)

        event["duration_ms"] = int((time.time() - start) * 1000)
        event["status"] = status_code_holder["status"]

        # Append to logfile
        try:
            with open(self.logfile, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(event, default=str) + "\n")
        except Exception:
            # Never raise in middleware audit demo
            pass
