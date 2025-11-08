"""Testes unitários mínimos para o skeleton RBAC/middleware.

Estes testes usam `TestClient` do FastAPI para validar comportamento de dependências
mock (headers `X-User` e `X-Roles`).
"""
from fastapi.testclient import TestClient
from backend.api.dashboard import app

client = TestClient(app)


def test_whoami_no_header():
    r = client.get("/api/v1/controls/me")
    assert r.status_code == 401


def test_whoami_with_header():
    r = client.get("/api/v1/controls/me", headers={"X-User": "presidente", "X-Roles": "presidente"})
    assert r.status_code == 200
    body = r.json()
    assert body["username"] == "presidente"
    assert "presidente" in body["roles"]


def test_admin_health_forbidden():
    r = client.get("/api/v1/controls/admin-health", headers={"X-User": "user1", "X-Roles": "presidente"})
    assert r.status_code == 403


def test_admin_health_ok():
    r = client.get("/api/v1/controls/admin-health", headers={"X-User": "admin", "X-Roles": "admin"})
    assert r.status_code == 200
