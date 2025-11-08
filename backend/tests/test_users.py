"""Testes para gerenciamento mínimo de usuários (CRUD).
Usam o token HMAC (Authorization Bearer) ou header X-User/X-Roles para autenticar.
"""
from fastapi.testclient import TestClient
from backend.api.dashboard import app
from backend.api.auth import create_token

client = TestClient(app)


def admin_headers():
    token = create_token({"username": "admin", "roles": ["admin"]}, expires_minutes=60)
    return {"Authorization": f"Bearer {token}"}


def test_create_get_delete_user():
    headers = admin_headers()
    payload = {"username": "u1", "roles": ["presidente"]}
    r = client.post('/api/v1/users', json=payload, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body['username'] == 'u1'

    r2 = client.get('/api/v1/users/u1', headers=headers)
    assert r2.status_code == 200
    assert r2.json()['username'] == 'u1'

    r3 = client.delete('/api/v1/users/u1', headers=headers)
    assert r3.status_code == 200

    r4 = client.get('/api/v1/users/u1', headers=headers)
    assert r4.status_code == 404


def test_list_requires_admin():
    # sem header -> 401
    r = client.get('/api/v1/users')
    assert r.status_code in (401, 403)
