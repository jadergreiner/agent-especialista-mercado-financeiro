"""Testes para autenticação baseada em token (mock HMAC)."""
from fastapi.testclient import TestClient
from backend.api.dashboard import app
from backend.api.auth import create_token

client = TestClient(app)


def test_token_creates_and_authenticates():
    token = create_token({"username": "alice", "roles": ["admin"]}, expires_minutes=5)
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/v1/controls/me", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["username"] == "alice"
    assert "admin" in body["roles"]


def test_token_expired():
    token = create_token({"username": "bob", "roles": ["presidente"]}, expires_minutes=-1)
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/v1/controls/me", headers=headers)
    assert r.status_code == 401
