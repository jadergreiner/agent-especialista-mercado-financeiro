"""Testes para Audit Trails: valida gravação e leitura de eventos."""
import sqlite3
import os
from fastapi.testclient import TestClient
from backend.api.dashboard import app
from backend.api.audit import DB_PATH

client = TestClient(app)


def _read_last_event():
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row


def test_request_generates_audit_event():
    # assegurar ausência anterior
    row_before = _read_last_event()
    r = client.get("/api/v1/dashboard/summary", headers={"X-User": "tester", "X-Roles": "presidente"})
    assert r.status_code == 200
    row_after = _read_last_event()
    assert row_after is not None
    # a última entrada deve pertencer ao usuário tester e ao endpoint solicitado
    assert row_after[2] == "tester"
    assert row_after[3] == "/api/v1/dashboard/summary"


def test_list_events_requires_auditor_role():
    r = client.get("/api/v1/audit/events")
    assert r.status_code == 401 or r.status_code == 403
    # com role auditor deve permitir
    r2 = client.get("/api/v1/audit/events", headers={"X-User": "auditor1", "X-Roles": "auditor"})
    assert r2.status_code == 200
