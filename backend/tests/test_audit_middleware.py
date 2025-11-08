import json
import os
import sys
import pathlib
import tempfile

# Ensure repo root is on sys.path for imports during tests
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.middleware.audit import AuditMiddleware


def test_audit_middleware_writes_log(tmp_path):
    # Create temp logfile path
    logfile = tmp_path / "audit.log"

    app = FastAPI()

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    # Wrap app with audit middleware
    app.add_middleware(AuditMiddleware, logfile=str(logfile))

    client = TestClient(app)
    resp = client.get("/ping")
    assert resp.status_code == 200

    # Ensure logfile created and contains at least one JSON line
    assert logfile.exists()
    content = logfile.read_text(encoding="utf-8").strip()
    assert content
    # Parse last line as JSON
    last_line = content.splitlines()[-1]
    obj = json.loads(last_line)
    assert obj.get("path") == "/ping"
    assert obj.get("status") == 200 or obj.get("status") is None
